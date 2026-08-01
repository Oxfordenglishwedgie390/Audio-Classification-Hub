/* ═══════════════════════════════════════════
   HERO SHADER — Three.js RawShaderMaterial
   Multicolor flowing audio waves with chromatic aberration
   ═══════════════════════════════════════════ */

function initHeroShader(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || typeof THREE === 'undefined') return;

  // Reduced-motion / WebGL fallback
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  } catch (e) {
    canvas.style.background =
      'radial-gradient(ellipse at center, rgba(99,102,241,0.25), #05070F 70%)';
    return;
  }

  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(canvas.clientWidth, canvas.clientHeight, false);

  const scene = new THREE.Scene();
  const camera = new THREE.Camera();
  camera.position.z = 1;

  const geometry = new THREE.PlaneGeometry(2, 2);

  const vertexShader = `
    precision highp float;
    attribute vec3 position;
    void main() {
      gl_Position = vec4(position, 1.0);
    }
  `;

  const fragmentShader = `
    precision highp float;
    uniform vec2  u_resolution;
    uniform float u_time;
    uniform float u_waveCount;
    uniform float u_amplitude;
    uniform float u_frequency;
    uniform float u_brightness;
    uniform float u_colorShift;

    vec3 palette(float t) {
      // deep purple -> magenta -> cyan -> gold
      vec3 a = vec3(0.5, 0.4, 0.6);
      vec3 b = vec3(0.5, 0.45, 0.5);
      vec3 c = vec3(1.0, 1.0, 1.0);
      vec3 d = vec3(0.66, 0.45, 0.20);
      return a + b * cos(6.28318 * (c * t + d));
    }

    void main() {
      vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / u_resolution.y;
      vec3 color = vec3(0.0);

      for (float i = 0.0; i < 8.0; i++) {
        if (i >= u_waveCount) break;
        float fi = i / u_waveCount;

        // wave offset per band
        float phase = u_time + fi * 6.2831;
        float offset = sin(uv.x * u_frequency + phase) * u_amplitude
                     + sin(uv.x * u_frequency * 0.5 - phase * 0.7) * u_amplitude * 0.5;

        // chromatic aberration: sample R/G/B with x offset
        float r = u_brightness / abs(uv.y - offset + u_colorShift * 0.06);
        float g = u_brightness / abs(uv.y - offset);
        float b = u_brightness / abs(uv.y - offset - u_colorShift * 0.06);

        vec3 bandColor = palette(fi + u_time * 0.05);
        color += vec3(r, g, b) * bandColor;
      }

      // central brightness bloom, fade at edges
      float falloff = exp(-uv.y * uv.y * 1.4);
      color *= falloff;

      // subtle vignette
      color *= smoothstep(1.6, 0.2, length(uv) * 0.7);

      gl_FragColor = vec4(color, 1.0);
    }
  `;

  const uniforms = {
    u_resolution: { value: new THREE.Vector2(canvas.clientWidth, canvas.clientHeight) },
    u_time: { value: 0 },
    u_waveCount: { value: 6.0 },
    u_amplitude: { value: 0.12 },
    u_frequency: { value: 1.8 },
    u_brightness: { value: 0.006 },
    u_colorShift: { value: 0.15 },
  };

  const material = new THREE.RawShaderMaterial({
    vertexShader,
    fragmentShader,
    uniforms,
  });

  const mesh = new THREE.Mesh(geometry, material);
  scene.add(mesh);

  function resize() {
    const w = canvas.clientWidth, h = canvas.clientHeight;
    renderer.setSize(w, h, false);
    uniforms.u_resolution.value.set(w * renderer.getPixelRatio(), h * renderer.getPixelRatio());
  }
  window.addEventListener('resize', resize);
  resize();

  let scrollFade = 1;
  window.addEventListener('scroll', () => {
    scrollFade = Math.max(0.15, 1 - window.scrollY / (window.innerHeight * 0.9));
  });

  function animate() {
    if (!reduced) {
      uniforms.u_time.value += 0.008;
    }
    uniforms.u_brightness.value = 0.006 * scrollFade;
    renderer.render(scene, camera);
    requestAnimationFrame(animate);
  }
  animate();

  // Static fallback look for reduced motion
  if (reduced) {
    renderer.render(scene, camera);
  }
}
