import numpy as np

import moderngl
import os

import moderngl_window as mglw


class Example(mglw.WindowConfig):
    gl_version = (3, 3)
    title = "ModernGL Example"
    window_size = (1280, 720)
    aspect_ratio = 16 / 9
    resizable = True

    resource_dir = os.path.normpath(os.path.join(__file__, '../../data'))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def run(cls):
        mglw.run_window_config(cls)
from pyrr import matrix44


class Particles(Example):
    title = "Particle System Emitter"
    gl_version = (3, 3)
    aspect_ratio = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Renders particles to the screen
        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330
                uniform mat4 projection;
                in vec2 in_pos;
                in vec3 in_color;
                out vec3 color;
                void main() {
                    gl_Position = projection * vec4(in_pos, 0.0, 1.0);
                    color = in_color;
                }
            ''',
            fragment_shader='''
                #version 330
                out vec4 f_color;
                in vec3 color;
                void main() {
                    f_color = vec4(color, 1.0);
                }
            ''',
        )

        # Animates / transforms the particles per frame
        self.transform = self.ctx.program(
            vertex_shader='''
            #version 330
            in vec2 in_pos;
            in vec2 in_vel;
            in vec3 in_color;
            out vec2 vs_vel;
            out vec3 vs_color;
            void main() {
                gl_Position = vec4(in_pos, 0.0, 1.0);
                vs_vel = in_vel;
                vs_color = in_color;
            }
            ''',
            geometry_shader='''
            #version 330
            layout(points) in;
            layout(points, max_vertices = 1) out;
            uniform float gravity;
            uniform float ft;
            in vec2 vs_vel[1];
            in vec3 vs_color[1];
            out vec2 out_pos;
            out vec2 out_vel;
            out vec3 out_color;
            void main() {
                vec2 pos = gl_in[0].gl_Position.xy;
                vec2 velocity = vs_vel[0];
                if (pos.y > -1.0) {
                    vec2 vel = velocity + vec2(0.0, gravity);
                    out_pos = pos + vel * ft;
                    out_vel = vel;
                    out_color = vs_color[0];
                    EmitVertex();
                    EndPrimitive();
                }
            }
            ''',
            varyings=['out_pos', 'out_vel', 'out_color'],
        )
        self.mouse_pos = 0, 0
        self.prog['projection'].write(self.projection)
        self.transform['gravity'].value = -.01  # affects the velocity of the particles over time
        self.ctx.point_size = self.wnd.pixel_ratio * 2 # point size

        self.N = 250  # particle count
        self.active_particles = self.N // 100  # Initial / current number of active particles
        self.max_emit_count = self.N // 100  # Maximum number of particles to emit per frame
        self.stride = 28  # byte stride for each vertex
        self.floats = 7
        # Note that passing dynamic=True probably doesn't mean anything to most drivers today
        self.vbo1 = self.ctx.buffer(reserve=self.N * self.stride)
        self.vbo2 = self.ctx.buffer(reserve=self.N * self.stride)
        # Write some initial particles
        self.vbo1.write(np.fromiter(self.gen_particles(self.active_particles), count=self.active_particles * self.floats, dtype='f4'))

        # Transform vaos. We transform data back and forth to avoid buffer copy
        self.transform_vao1 = self.ctx.vertex_array(
            self.transform,
            [(self.vbo1, '2f 2f 3f', 'in_pos', 'in_vel', 'in_color')],
        )
        self.transform_vao2 = self.ctx.vertex_array(
            self.transform,
            [(self.vbo2, '2f 2f 3f', 'in_pos', 'in_vel', 'in_color')],
        )

        # Render vaos. The render to screen version of the tranform vaos above
        self.render_vao1 = self.ctx.vertex_array(
            self.prog,
            [(self.vbo1, '2f 2x4 3f', 'in_pos', 'in_color')],
        )
        self.render_vao2 = self.ctx.vertex_array(
            self.prog,
            [(self.vbo2, '2f 2x4 3f', 'in_pos', 'in_color')],
        )

        # Setup for emit method #2. The emit buffer size is only max_emit_count.
        self.emit_buffer_elements = self.max_emit_count
        self.emit_buffer = self.ctx.buffer(reserve=self.emit_buffer_elements * self.stride)
        self.emit_buffer_prog = self.ctx.program(  # Siple shader just emitting a buffer
            vertex_shader='''
            # version 330
            in vec2 in_pos;
            in vec2 in_vel;
            in vec3 in_color;
            out vec2 out_pos;
            out vec2 out_vel;
            out vec3 out_color;
            void main() {
                out_pos = in_pos;
                out_vel = in_vel;
                out_color = in_color;
            }
            ''',
            varyings=['out_pos', 'out_vel', 'out_color'],
        )
        self.emit_buffer_vao = self.ctx.vertex_array(
            self.emit_buffer_prog,
            [(self.emit_buffer, '2f 2f 3f', 'in_pos', 'in_vel', 'in_color')],
        )

        # Setup for method #3: GPU emitting
        self.gpu_emitter_prog = self.ctx.program(
            vertex_shader='''
            # version 330
            #define M_PI 3.1415926535897932384626433832795
            uniform vec2 mouse_pos;
            uniform float time;
            out vec2 out_pos;
            out vec2 out_vel;
            out vec3 out_color;
            float rand(float n){return fract(sin(n) * 43758.5453123);}
            void main() {
                float a = mod(time * gl_VertexID, M_PI * 2);
                float r = clamp(rand(time + gl_VertexID), 0.1, 0.9);
                out_pos = mouse_pos;
                out_vel = vec2(sin(a), cos(a)) * r;
                out_color = vec3(rand(time * 1.3 + gl_VertexID), rand(time * 3.4 + gl_VertexID), rand(time * 2.0 + gl_VertexID));
            }
            ''',
            varyings=['out_pos', 'out_vel', 'out_color'],
        )
        self.gpu_emitter_vao = self.ctx._vertex_array(self.gpu_emitter_prog, [])

        # Query object to inspect render calls
        self.query = self.ctx.query(primitives=True)

    def render(self, time, frame_time):
        self.transform['ft'].value = max(frame_time, 0.02)
        
        # Cycle emit methods per frame
        method = self.wnd.frames % 3 + 1
        # ---> HARDCODE METHOD HERE <---
        # method = 3
        if method == 1:
            self.emit_cpu_simple(time, frame_time)
        elif method == 2:
            self.emit_cpu_buffer(time, frame_time)
        elif method == 3:
            self.emit_gpu(time, frame_time)

        # Swap around objects for next frame
        self.transform_vao1, self.transform_vao2 = self.transform_vao2, self.transform_vao1
        self.render_vao1, self.render_vao2 = self.render_vao2, self.render_vao1
        self.vbo1, self.vbo2 = self.vbo2, self.vbo1

        err = self.ctx.error 
        if err != "GL_NO_ERROR":
            print(err)

    def emit_cpu_simple(self, time, frame_time):
        """Method #1
        Emit new particles simply by writing new particles to
        to the end of the buffer. This will most likely cause
        the entire buffer to be re-written to the gpu, but is
        probably acceptable for smaller particle amounts.
        """
        # Transform all particles recoding how many elements were emitted by geometry shader
        with self.query:
            self.transform_vao1.transform(self.vbo2, moderngl.POINTS, vertices=self.active_particles)

        # Emit new particles if needed simply by writing to the end of the buffer (cpu)
        emit_count = min(self.N - self.query.primitives, self.max_emit_count)
        if emit_count > 0:
            self.vbo2.write(
                np.fromiter(self.gen_particles(emit_count), 'f4', count=emit_count * self.floats),
                offset=self.query.primitives * self.stride,
            )

        self.active_particles = self.query.primitives + emit_count
        self.render_vao2.render(moderngl.POINTS, vertices=self.active_particles)

    def emit_cpu_buffer(self, time, frame_time):
        """Method #2
        Emit new particles by writing new ones with the cpu
        to a separate emit buffer. This buffer can be smaller
        than the main particle buffer meaning less buffer
        data to stream to the gpu per frame.
        """
        # Transform all particles recoding how many elements were emitted by geometry shader
        with self.query:
            self.transform_vao1.transform(self.vbo2, moderngl.POINTS, vertices=self.active_particles)

        emit_count = min(self.N - self.query.primitives, self.emit_buffer_elements, self.max_emit_count)
        if emit_count > 0:
            self.emit_buffer.write(
                np.fromiter(self.gen_particles(emit_count), 'f4', count=emit_count * self.floats)
            )
            self.emit_buffer_vao.transform(self.vbo2, vertices=emit_count, buffer_offset=self.query.primitives * self.stride)

        self.active_particles = self.query.primitives + emit_count
        self.render_vao2.render(moderngl.POINTS, vertices=self.active_particles)

    def emit_gpu(self, time, frame_time):
        """Method #3
        Emit new particles using a shader.
        """
        # Transform all particles recoding how many elements were emitted by geometry shader
        with self.query:
            self.transform_vao1.transform(self.vbo2, moderngl.POINTS, vertices=self.active_particles)

        emit_count = min(self.N - self.query.primitives, self.emit_buffer_elements, self.max_emit_count)
        if emit_count > 0:
            self.gpu_emitter_prog['mouse_pos'].value = self.mouse_pos
            self.gpu_emitter_prog['time'].value = max(time, 0)
            self.gpu_emitter_vao.transform(self.vbo2, vertices=emit_count, buffer_offset=self.query.primitives * self.stride)

        self.active_particles = self.query.primitives + emit_count
        self.render_vao2.render(moderngl.POINTS, vertices=self.active_particles)

    def gen_particles(self, n):
        for _ in range(n):
            # Current mouse position (2 floats)
            yield self.mouse_pos[0]
            yield self.mouse_pos[1]
            # Random velocity (2 floats)
            a = np.random.uniform(0.0, np.pi * 2.0)
            r = np.random.uniform(0.1, 0.9)
            yield np.cos(a) * r
            yield np.sin(a) * r
            # Random color (3 floats)
            yield np.random.uniform(0.0, 1.0)
            yield np.random.uniform(0.0, 1.0)
            yield np.random.uniform(0.0, 1.0)

    @property
    def projection(self):
        return matrix44.create_orthogonal_projection(
            -self.wnd.aspect_ratio, self.wnd.aspect_ratio,
            -1, 1,
            -1, 1,
            dtype='f4',
        )

    def resize(self, width, height):
        """Handle window resizing"""
        self.prog['projection'].write(self.projection)

    def key_event(self, key, action, modifiers):
        keys = self.wnd.keys

        if action == keys.ACTION_PRESS and key == keys.F1:
            screenshot.create(self.wnd.fbo)


if __name__ == '__main__':
    Particles.run()