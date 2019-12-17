#version 130

in vec2 texture_coords;

out vec3 normal;
out vec3 camera;

void main() {
    normal = normalize(gl_NormalMatrix * gl_Normal);
    camera = normalize(vec3(gl_ModelViewMatrix * gl_Vertex));

    gl_TexCoord[0].xy = texture_coords;
    gl_Position = ftransform();
}