const SLIDER_IMAGES = [
  { id: "hero", label: "Besties cartoon", src: "/assets/brand/hero.png" },
  { id: "healing", label: "Healing inbox", src: "/assets/features/healing-inbox.jpg" },
  { id: "realtime", label: "Real-time realization", src: "/assets/features/real-time-realization.jpg" },
];

const SLIDER_DIFFICULTIES = {
  easy: { label: "Easy", size: 3 },
  med: { label: "Med", size: 4 },
  hard: { label: "Hard", size: 5 },
};

const SLIDER_WIN_MESSAGES = {
  hero: [
    { title: "Bestie, you did that!", body: "It's time for Chittin' and Chattin'!" },
    { title: "Puzzle complete!", body: "Sydney and M are back - grab your sip and press play." },
  ],
  healing: [
    { title: "So soft, so solved.", body: "Your gentle moment is whole again." },
    { title: "Cozy win!", body: "Take a breath - you put it all back together." },
  ],
  realtime: [
    { title: "Real-time realization!", body: "Every piece clicked into place." },
    { title: "You solved it!", body: "That little aha feels so good." },
  ],
};

function sliderEmptyTile(size) {
  return size * size - 1;
}

function sliderSolvedState(size) {
  return Array.from({ length: size * size }, (_, i) => i);
}

function sliderIndexToRowCol(index, size) {
  return { row: Math.floor(index / size), col: index % size };
}

function sliderIsAdjacent(a, b, size) {
  const ar = Math.floor(a / size);
  const ac = a % size;
  const br = Math.floor(b / size);
  const bc = b % size;
  return Math.abs(ar - br) + Math.abs(ac - bc) === 1;
}

function sliderCanSlideToward(clickIdx, emptyIdx, size) {
  if (clickIdx === emptyIdx) return false;
  const click = sliderIndexToRowCol(clickIdx, size);
  const empty = sliderIndexToRowCol(emptyIdx, size);
  return click.row === empty.row || click.col === empty.col;
}

function sliderSlideToward(state, clickIdx, size) {
  const empty = sliderEmptyTile(size);
  const emptyIdx = state.indexOf(empty);
  if (!sliderCanSlideToward(clickIdx, emptyIdx, size)) return null;

  const sameRow = Math.floor(clickIdx / size) === Math.floor(emptyIdx / size);
  const step = sameRow
    ? (clickIdx < emptyIdx ? 1 : -1)
    : (clickIdx < emptyIdx ? size : -size);
  let tilesMoved = 0;
  let i = clickIdx;
  while (i !== emptyIdx) {
    tilesMoved += 1;
    i += step;
  }

  const next = state.slice();

  if (sameRow) {
    if (clickIdx < emptyIdx) {
      for (let i = emptyIdx; i > clickIdx; i -= 1) {
        next[i] = next[i - 1];
      }
      next[clickIdx] = empty;
    } else {
      for (let i = emptyIdx; i < clickIdx; i += 1) {
        next[i] = next[i + 1];
      }
      next[clickIdx] = empty;
    }
    return { state: next, tilesMoved };
  }

  if (clickIdx < emptyIdx) {
    for (let i = emptyIdx; i > clickIdx; i -= size) {
      next[i] = next[i - size];
    }
    next[clickIdx] = empty;
  } else {
    for (let i = emptyIdx; i < clickIdx; i += size) {
      next[i] = next[i + size];
    }
    next[clickIdx] = empty;
  }

  return { state: next, tilesMoved };
}

function sliderCreateRng(seed) {
  if (seed == null || seed === "") return Math.random;
  let state = Number(seed) >>> 0 || 1;
  return () => {
    state = (state * 1664525 + 1013904223) >>> 0;
    return state / 4294967296;
  };
}

function sliderShuffleBoard(size, rng = Math.random) {
  const state = sliderSolvedState(size);
  const empty = sliderEmptyTile(size);
  let emptyIdx = state.indexOf(empty);
  const scrambleMoves = size * size * 40;

  for (let i = 0; i < scrambleMoves; i += 1) {
    const neighbors = [];
    const { row, col } = sliderIndexToRowCol(emptyIdx, size);
    if (row > 0) neighbors.push(emptyIdx - size);
    if (row < size - 1) neighbors.push(emptyIdx + size);
    if (col > 0) neighbors.push(emptyIdx - 1);
    if (col < size - 1) neighbors.push(emptyIdx + 1);

    const pick = neighbors[Math.floor(rng() * neighbors.length)];
    state[emptyIdx] = state[pick];
    state[pick] = empty;
    emptyIdx = pick;
  }

  return state;
}

function sliderIsWin(state) {
  for (let i = 0; i < state.length; i += 1) {
    if (state[i] !== i) return false;
  }
  return true;
}

function sliderTileBackgroundStyle(tileIndex, size, imageSrc) {
  const { row, col } = sliderIndexToRowCol(tileIndex, size);
  const pct = size > 1 ? 100 / (size - 1) : 0;
  const x = col * pct;
  const y = row * pct;
  return `background-image:url('${imageSrc}');background-size:${size * 100}% ${size * 100}%;background-position:${x}% ${y}%`;
}

function sliderPickRandomImage(images, rng = Math.random, excludeId) {
  const pool = excludeId ? images.filter((img) => img.id !== excludeId) : images.slice();
  const list = pool.length ? pool : images.slice();
  return list[Math.floor(rng() * list.length)];
}

function sliderResolveImage(images, imageId) {
  if (!imageId) return null;
  return images.find((img) => img.id === imageId) || null;
}

function sliderParseOptions(search, images = SLIDER_IMAGES, difficulties = SLIDER_DIFFICULTIES) {
  const params = new URLSearchParams(search || "");
  const diff = params.get("diff");
  const image = params.get("image");
  const seed = params.get("seed");

  return {
    difficulty: diff && difficulties[diff] ? diff : null,
    image: sliderResolveImage(images, image),
    seed: seed != null && seed !== "" ? seed : null,
  };
}

function sliderPickWinMessage(imageId, rng = Math.random, messages = SLIDER_WIN_MESSAGES) {
  const list = messages[imageId] || messages.hero;
  return list[Math.floor(rng() * list.length)];
}

const SliderPuzzleLogic = {
  SLIDER_IMAGES,
  SLIDER_DIFFICULTIES,
  SLIDER_WIN_MESSAGES,
  sliderEmptyTile,
  sliderSolvedState,
  sliderIndexToRowCol,
  sliderIsAdjacent,
  sliderCanSlideToward,
  sliderSlideToward,
  sliderCreateRng,
  sliderShuffleBoard,
  sliderIsWin,
  sliderTileBackgroundStyle,
  sliderPickRandomImage,
  sliderResolveImage,
  sliderParseOptions,
  sliderPickWinMessage,
};

if (typeof window !== "undefined") {
  window.SliderPuzzleLogic = SliderPuzzleLogic;
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = SliderPuzzleLogic;
}
