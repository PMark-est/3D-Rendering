#version 330 core

layout (location = 0) out vec4 fragColor;

in vec3 normal;
in vec3 fragPos;
in vec4 shadowCoord;

struct Light {
    vec3 position_v;
    vec3 Ia;
    vec3 Id;
    vec3 Is;
};

uniform Light light; // esimene 'Light' tuleb eelnevast 
uniform vec3 camPos;
uniform sampler2DShadow shadowMap;

float getShadow() {
    float shadow = textureProj(shadowMap, shadowCoord);
    return shadow;
}

vec3 getLight(vec3 color) {  // Valguse/varjude loomine
    vec3 Normal = normalize(normal);

    // ambient light - üldine valgustugevus üle terve pildi, ei sõltu mingist punktist
    vec3 ambient = light.Ia;

    // diffuse light - hajuv valgus kindlast punktist (laelambist tulevad kiired peegeldvad ühtlaselt igas suunas)
    vec3 lightDir = normalize(light.position_v - fragPos);
    float diff = max(0, dot(lightDir, Normal));
    vec3 diffuse = diff * light.Id;

    // specular light - punktist peegelduv valgus kindla nurga alt (nagu peegel, kiired ei haju laiali vaid jäävad kindla nurga alla)
    vec3 viewDir = normalize(camPos - fragPos);
    vec3 reflectDir = reflect(-lightDir, Normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0), 32);
    vec3 specular = spec * light.Is;

    // varjud
    float shadow = getShadow();

    return color * (ambient + (diffuse + specular) * shadow);
}

void main(){
    vec3 color = vec3(1, 0, 0); // Kuubi värv
    color = getLight(color);
    fragColor = vec4(color, 1.0);
}