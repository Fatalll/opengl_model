#version 130

uniform vec3 light = vec3(0.1, 0.1, 1);

in vec3 normal;
in vec3 camera;

uniform sampler2D noise;
uniform float dissolve_threshold = 1;

void main() {
    vec4 color = texture(noise, gl_TexCoord[0].xy);

    if (color[0] > dissolve_threshold) {
        discard;
    }

    gl_FragColor += (dot(normal, camera) + dot(normal, light)) * vec4(0, 0, 0.7, 1);
}