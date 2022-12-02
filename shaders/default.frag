#version 330 core

layout (location = 0) out vec4 fragColor;

in vec2 uv_0;
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
uniform sampler2D u_texture_0;
uniform sampler2DShadow shadowMap;
uniform vec2 u_resolution;

float lookup(float ox, float oy) {
    vec2 pixelOffset = 1 / u_resolution;
    return textureProj(shadowMap, shadowCoord + vec4(ox * pixelOffset.x * shadowCoord.w, oy * pixelOffset.y * shadowCoord.w, 0.0, 0.0));
}

// Õrnalt hägustatud joontega varjud
float getSoftShadowX16() {
    float shadow;
    float swidth = 1.0;
    float endp = swidth * 1.5;
    for (float y = -endp; y <= endp; y += swidth) {
        for (float x = -endp; x <= endp; x += swidth) {
            shadow += lookup(x, y);
        }
    }
    return shadow / 16.0;
}

// Pisut rohkem häguste joontega varjud
float getSoftShadowX64() {
    float shadow;
    float swidth = 0.6;
    float endp = swidth * 3.0 + swidth / 2.0;
    for (float y = -endp; y <= endp; y += swidth) {
        for (float x = -endp; x <= endp; x += swidth) {
            shadow += lookup(x, y);
        }
    }
    return shadow / 64;
}

// Kõige tavalisem varjude looja (teravad jooned)
// Hetkel ei ole seda vaja, kui kasutada ülemist X64 varjude loomist
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
    // float shadow = getShadow();
    float shadow = getSoftShadowX64();

    return color * (ambient + (diffuse + specular) * shadow);
}

void main(){
    vec3 color = texture(u_texture_0, uv_0).rgb; // Kuubi pilt/värv
    color = getLight(color);
    fragColor = vec4(color, 1.0);
}