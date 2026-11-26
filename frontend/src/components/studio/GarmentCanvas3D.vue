<template>
  <div ref="containerRef" class="canvas-wrapper"></div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import * as THREE from "three";

const props = defineProps({
  color: { type: String, default: "#1f2937" },
  roughness: { type: Number, default: 0.78 },
  size: { type: String, default: "L" },
  printingText: { type: String, default: "RE:FIT" },
  oversizedHood: { type: Boolean, default: true },
});

const containerRef = ref(null);
let renderer, scene, camera, garmentGroup, bodyMaterial, printMesh, animId;

const SIZE_SCALE = {
  XS: [0.86, 0.9, 0.88],
  S: [0.92, 0.94, 0.93],
  M: [0.97, 0.98, 0.97],
  L: [1.0, 1.0, 1.0],
  XL: [1.07, 1.04, 1.06],
  "2XL": [1.14, 1.08, 1.12],
  "3XL": [1.22, 1.12, 1.18],
};

function makePrintTexture(text) {
  const canvas = document.createElement("canvas");
  canvas.width = 512;
  canvas.height = 256;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#f9fafb";
  ctx.font = "bold 64px sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(text || "", 256, 128);
  const tex = new THREE.CanvasTexture(canvas);
  tex.needsUpdate = true;
  return tex;
}

onMounted(() => {
  const el = containerRef.value;
  scene = new THREE.Scene();
  scene.background = new THREE.Color("#0f172a");

  camera = new THREE.PerspectiveCamera(42, el.clientWidth / el.clientHeight, 0.1, 100);
  camera.position.set(0, 0.4, 4.4);

  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(el.clientWidth, el.clientHeight);
  renderer.setPixelRatio(window.devicePixelRatio);
  el.appendChild(renderer.domElement);

  scene.add(new THREE.AmbientLight(0xffffff, 0.85));
  const dirLight = new THREE.DirectionalLight(0xffffff, 1.1);
  dirLight.position.set(3, 5, 4);
  scene.add(dirLight);

  bodyMaterial = new THREE.MeshStandardMaterial({
    color: new THREE.Color(props.color),
    roughness: props.roughness,
    metalness: 0.05,
  });

  garmentGroup = new THREE.Group();

  // Base hoodie torso + sleeves + hood placeholder (swap with GLTFLoader .glb asset)
  const torso = new THREE.Mesh(new THREE.CylinderGeometry(0.75, 0.78, 1.7, 32), bodyMaterial);
  garmentGroup.add(torso);

  const leftSleeve = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.2, 1.35, 24), bodyMaterial);
  leftSleeve.position.set(-0.96, 0.12, 0);
  leftSleeve.rotation.z = 0.35;
  garmentGroup.add(leftSleeve);

  const rightSleeve = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.2, 1.35, 24), bodyMaterial);
  rightSleeve.position.set(0.96, 0.12, 0);
  rightSleeve.rotation.z = -0.35;
  garmentGroup.add(rightSleeve);

  const hood = new THREE.Mesh(new THREE.SphereGeometry(0.55, 24, 24), bodyMaterial);
  hood.position.set(0, 1.05, -0.15);
  hood.name = "hood";
  garmentGroup.add(hood);

  const printMat = new THREE.MeshBasicMaterial({
    map: makePrintTexture(props.printingText),
    transparent: true,
  });
  printMesh = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 0.45), printMat);
  printMesh.position.set(0, 0.25, 0.78);
  garmentGroup.add(printMesh);

  scene.add(garmentGroup);

  const animate = () => {
    animId = requestAnimationFrame(animate);
    garmentGroup.rotation.y += 0.005;
    renderer.render(scene, camera);
  };
  animate();
});

watch(
  () => [props.color, props.roughness, props.size, props.printingText, props.oversizedHood],
  () => {
    if (!bodyMaterial || !garmentGroup) return;
    bodyMaterial.color.set(props.color);
    bodyMaterial.roughness = props.roughness;
    const [sx, sy, sz] = SIZE_SCALE[props.size] || [1, 1, 1];
    garmentGroup.scale.set(sx, sy, sz);
    const hood = garmentGroup.getObjectByName("hood");
    if (hood) hood.scale.setScalar(props.oversizedHood ? 1.18 : 0.92);
    if (printMesh) {
      printMesh.material.map?.dispose();
      printMesh.material.map = makePrintTexture(props.printingText);
      printMesh.material.needsUpdate = true;
    }
  }
);

onBeforeUnmount(() => {
  cancelAnimationFrame(animId);
  renderer?.dispose();
});
</script>

<style scoped>
.canvas-wrapper {
  width: 100%;
  height: 100%;
  min-height: 480px;
  border-radius: 16px;
  overflow: hidden;
}
</style>
