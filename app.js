const TOTAL_BLOCKS = 192;
const BLOCK_MB = 32;
const memory = [];
const processColors = ["#ff2bd6", "#8d4dff", "#00e5ff", "#4dffb5", "#ffb84d"];
let nextProcessId = 1;
let pageFaults = 0;
let ioRate = 0;
let defragging = false;

const grid = document.querySelector("#memoryGrid");
const buildingCity = document.querySelector("#buildingCity");
const skyline = document.querySelector("#skyline");
const statusText = document.querySelector("#statusText");
const stressInput = document.querySelector("#cityStress");

const metrics = {
  population: document.querySelector("#populationMetric"),
  holes: document.querySelector("#holesMetric"),
  fragmentation: document.querySelector("#fragmentationMetric"),
  faults: document.querySelector("#faultsMetric"),
  io: document.querySelector("#ioMetric")
};

function seedCity() {
  for (let i = 0; i < TOTAL_BLOCKS; i++) {
    memory.push({ used: false, processId: null, color: null });
  }

  for (let i = 0; i < 28; i++) {
    allocateProcess(randomInt(2, 10), true);
  }
  for (let i = 0; i < 11; i++) {
    freeRandomProcess(true);
  }
  render();
  setStatus("DataCity arrancó con barrios fragmentados listos para estudiar.");
}

function allocateProcess(size = randomInt(2, 12), silent = false) {
  const freeIndexes = memory
    .map((block, index) => (!block.used ? index : -1))
    .filter(index => index !== -1);

  if (freeIndexes.length < size) {
    setStatus("No hay lotes suficientes: intenta desfragmentar la ciudad.");
    return false;
  }

  const stress = Number(stressInput.value);
  const processId = nextProcessId++;
  const color = processColors[processId % processColors.length];
  const chosen = [];
  let usedContiguousRun = false;

  if (Math.random() > stress / 12) {
    const start = findContiguousFreeRun(size);
    if (start !== -1) {
      for (let i = start; i < start + size; i++) chosen.push(i);
      usedContiguousRun = true;
    }
  }

  while (chosen.length < size) {
    const randomFree = freeIndexes.splice(randomInt(0, freeIndexes.length - 1), 1)[0];
    if (!chosen.includes(randomFree)) chosen.push(randomFree);
  }

  chosen.forEach(index => {
    memory[index] = { used: true, processId, color };
  });

  pageFaults += randomInt(1, 8) + Math.round(stress / 2);
  ioRate += size * randomInt(2, 8);
  if (!silent) setStatus(`Nuevo edificio de ${size * BLOCK_MB} MB construido en lotes ${usedContiguousRun ? "continuos" : "dispersos"}.`);
  render();
  return true;
}

function freeRandomProcess(silent = false) {
  const processes = [...new Set(memory.filter(block => block.used).map(block => block.processId))];
  if (!processes.length) return;

  const target = processes[randomInt(0, processes.length - 1)];
  let removed = 0;
  memory.forEach((block, index) => {
    if (block.processId === target) {
      memory[index] = { used: false, processId: null, color: null };
      removed++;
    }
  });

  pageFaults += randomInt(0, 4);
  ioRate += removed * randomInt(1, 5);
  if (!silent) setStatus(`Demolición completada: ${removed * BLOCK_MB} MB quedaron como zona baldía.`);
  render();
}

function defragmentCity() {
  if (defragging) return;
  defragging = true;
  setStatus("Desfragmentando: drones de mudanza reacomodan edificios al distrito central...");

  buildingCity.classList.add("is-defragging");
  document.querySelectorAll(".block.used").forEach(block => block.classList.add("moving"));
  document.querySelectorAll(".building").forEach(building => building.classList.add("moving"));

  setTimeout(() => {
    const usedBlocks = memory.filter(block => block.used);
    memory.forEach((_, index) => {
      memory[index] = usedBlocks[index]
        ? { ...usedBlocks[index] }
        : { used: false, processId: null, color: null };
    });
    pageFaults = Math.max(0, pageFaults - randomInt(4, 12));
    ioRate += usedBlocks.length * 2;
    defragging = false;
    render();
    setStatus("Desfragmentación completa: queda un mega-lote libre para procesos grandes.");
    setTimeout(() => {
      buildingCity.classList.remove("is-defragging");
      document.querySelectorAll(".building").forEach(building => building.classList.remove("moving"));
    }, 900);
  }, 950);
}

function simulateBurst() {
  const stress = Number(stressInput.value);
  const actions = randomInt(3, 7);
  for (let i = 0; i < actions; i++) {
    Math.random() > 0.45 ? allocateProcess(randomInt(1, stress + 3), true) : freeRandomProcess(true);
  }
  pageFaults += randomInt(8, 22) + stress;
  ioRate += randomInt(80, 240);
  setStatus("Tormenta E/S: lecturas y escrituras aceleraron el tráfico de DataCity.");
  render();
}

function render() {
  renderGrid();
  renderBuildings();
  renderSkyline();
  updateMetrics();
}

function renderGrid() {
  grid.innerHTML = "";
  memory.forEach((block, index) => {
    const cell = document.createElement("div");
    cell.className = `block${block.used ? " used" : ""}`;
    cell.title = block.used
      ? `Lote ${index}: ocupado por proceso ${block.processId}`
      : `Lote ${index}: libre`;
    if (block.used) cell.style.background = `linear-gradient(180deg, ${block.color}, #6d1cff 55%, #12133e)`;
    grid.appendChild(cell);
  });
}

function renderBuildings() {
  const processes = getProcessSummaries();
  const activeIds = new Set(processes.map(process => String(process.id)));

  [...buildingCity.querySelectorAll(".building")].forEach(building => {
    if (!activeIds.has(building.dataset.processId)) building.remove();
  });

  processes.forEach(process => {
    let building = buildingCity.querySelector(`[data-process-id="${process.id}"]`);
    if (!building) {
      building = document.createElement("article");
      building.className = "building entering";
      building.dataset.processId = process.id;
      building.innerHTML = `
        <span class="antenna"></span>
        <span class="memory-label"></span>
        <span class="window-grid"></span>
        <span class="door"></span>
      `;
      buildingCity.appendChild(building);
      requestAnimationFrame(() => building.classList.remove("entering"));
    }

    const sizeMb = process.size * BLOCK_MB;
    const height = Math.min(250, 48 + process.size * 16);
    const width = Math.min(92, 34 + process.size * 4);
    const col = process.anchor % 24;
    const row = Math.floor(process.anchor / 24);
    const x = 2 + (col / 23) * 88;
    const y = 12 + row * 7;

    building.style.setProperty("--building-color", process.color);
    building.style.left = `${x}%`;
    building.style.width = `${width}px`;
    building.style.height = `${height}px`;
    building.style.transform = `translateX(-50%) translateY(-${y}px)`;
    building.style.zIndex = String(100 + row + process.size);
    building.title = `Proceso ${process.id}: ${sizeMb} MB en ${process.size} bloques`;
    building.querySelector(".memory-label").textContent = `${sizeMb} MB`;
    building.querySelector(".window-grid").style.setProperty("--floors", Math.max(2, process.size));
  });
}

function renderSkyline() {
  skyline.innerHTML = "";
  const processes = getProcessSummaries();
  processes.forEach(process => {
    const tower = document.createElement("span");
    tower.className = "tower";
    tower.style.height = `${Math.min(190, 32 + process.size * 14)}px`;
    tower.style.flexGrow = String(Math.max(1, process.size / 2));
    tower.style.background = `linear-gradient(180deg, ${process.color}, #102dff)`;
    tower.title = `Proceso ${process.id}: ${process.size * BLOCK_MB} MB`;
    skyline.appendChild(tower);
  });

  for (let i = processes.length; i < 34; i++) {
    const emptyLot = document.createElement("span");
    emptyLot.className = "tower free";
    emptyLot.style.height = `${8 + ((i * 5) % 30)}px`;
    skyline.appendChild(emptyLot);
  }
}

function getProcessSummaries() {
  const processes = new Map();
  memory.forEach((block, index) => {
    if (!block.used) return;
    if (!processes.has(block.processId)) {
      processes.set(block.processId, {
        id: block.processId,
        color: block.color,
        size: 0,
        indexes: [],
        anchor: index
      });
    }
    const process = processes.get(block.processId);
    process.size++;
    process.indexes.push(index);
    process.anchor = Math.min(process.anchor, index);
  });
  return [...processes.values()].sort((a, b) => a.anchor - b.anchor);
}

function updateMetrics() {
  const used = memory.filter(block => block.used).length;
  const holes = countFreeHoles();
  const free = TOTAL_BLOCKS - used;
  const fragmentation = free === 0 ? 0 : Math.round((1 - largestFreeRun() / free) * 100);

  metrics.population.textContent = `${used * BLOCK_MB} MB`;
  metrics.holes.textContent = holes;
  metrics.fragmentation.textContent = `${fragmentation}%`;
  metrics.faults.textContent = `${pageFaults}/s`;
  metrics.io.textContent = `${ioRate} MB/s`;
}

function countFreeHoles() {
  let holes = 0;
  let inHole = false;
  memory.forEach(block => {
    if (!block.used && !inHole) {
      holes++;
      inHole = true;
    }
    if (block.used) inHole = false;
  });
  return holes;
}

function largestFreeRun() {
  let best = 0;
  let current = 0;
  memory.forEach(block => {
    if (!block.used) {
      current++;
      best = Math.max(best, current);
    } else {
      current = 0;
    }
  });
  return best;
}

function findContiguousFreeRun(size) {
  let run = 0;
  for (let i = 0; i < memory.length; i++) {
    run = memory[i].used ? 0 : run + 1;
    if (run >= size) return i - size + 1;
  }
  return -1;
}

function setStatus(message) {
  statusText.textContent = message;
}

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

document.querySelector("#allocateBtn").addEventListener("click", () => allocateProcess());
document.querySelector("#freeBtn").addEventListener("click", () => freeRandomProcess());
document.querySelector("#burstBtn").addEventListener("click", simulateBurst);
document.querySelector("#defragBtn").addEventListener("click", defragmentCity);

setInterval(() => {
  if (!defragging) {
    pageFaults = Math.max(0, pageFaults + randomInt(-3, 4));
    ioRate = Math.max(0, Math.round(ioRate * 0.88) + randomInt(0, 12));
    updateMetrics();
  }
}, 1400);

seedCity();
