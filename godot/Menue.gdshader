shader_type canvas_item;

// Hiermit kannst du die Stärke im Inspektor einstellen
uniform float blur_amount: hint_range(0.0, 5.0) = 2.0;

void fragment() {
    // textureLod sorgt für den Weichzeichner-Effekt
    COLOR = textureLod(TEXTURE, UV, blur_amount);
}