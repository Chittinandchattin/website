import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import path from "node:path";

const require = createRequire(import.meta.url);
const logicPath = path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "assets", "js", "slider-puzzle-logic.js");
const logic = require(logicPath);

const {
  SLIDER_IMAGES,
  SLIDER_DIFFICULTIES,
  sliderEmptyTile,
  sliderSolvedState,
  sliderIsAdjacent,
  sliderCanSlideToward,
  sliderSlideToward,
  sliderCreateRng,
  sliderShuffleBoard,
  sliderIsWin,
  sliderPickRandomImage,
  sliderResolveImage,
  sliderParseOptions,
  sliderPickWinMessage,
} = logic;

let passed = 0;
let failed = 0;

function assert(condition, message) {
  if (condition) {
    passed += 1;
    return;
  }
  failed += 1;
  console.error(`FAIL: ${message}`);
}

assert(SLIDER_DIFFICULTIES.easy.size === 3, "easy is 3x3");
assert(SLIDER_DIFFICULTIES.med.size === 4, "med is 4x4");
assert(SLIDER_DIFFICULTIES.hard.size === 5, "hard is 5x5");
assert(sliderEmptyTile(3) === 8, "3x3 empty tile is 8");
assert(sliderEmptyTile(5) === 24, "5x5 empty tile is 24");
assert(sliderSolvedState(3).join(",") === "0,1,2,3,4,5,6,7,8", "solved state for 3x3");
assert(sliderIsAdjacent(0, 1, 3), "0 and 1 are adjacent");
assert(!sliderIsAdjacent(0, 2, 3), "0 and 2 are not adjacent");
assert(sliderIsWin(sliderSolvedState(3)), "solved board wins");

const rng = sliderCreateRng("42");
const shuffled = sliderShuffleBoard(3, rng);
assert(!sliderIsWin(shuffled), "shuffled 3x3 is not solved");
assert(shuffled.length === 9, "shuffled board length");

const rng2 = sliderCreateRng("42");
const shuffled2 = sliderShuffleBoard(3, rng2);
assert(shuffled.join(",") === shuffled2.join(","), "seeded shuffle is deterministic");

const forced = sliderResolveImage(SLIDER_IMAGES, "healing");
assert(forced?.id === "healing", "resolve healing image");

const opts = sliderParseOptions("?image=realtime&diff=hard&seed=7");
assert(opts.image?.id === "realtime", "parse image param");
assert(opts.difficulty === "hard", "parse diff param");
assert(opts.seed === "7", "parse seed param");

const pickRng = sliderCreateRng("99");
const first = sliderPickRandomImage(SLIDER_IMAGES, pickRng);
const second = sliderPickRandomImage(SLIDER_IMAGES, pickRng, first.id);
assert(first.id !== second.id || SLIDER_IMAGES.length === 1, "pick avoids previous when possible");
assert(SLIDER_IMAGES.some((img) => img.id === second.id), "picked image is valid");

const rowState = [0, 1, 8, 3, 4, 5, 6, 7, 2];
const rowSlide = sliderSlideToward(rowState, 0, 3);
assert(rowSlide?.state.join(",") === "8,0,1,3,4,5,6,7,2", "row multi-slide shifts tiles toward empty");
assert(rowSlide?.tilesMoved === 2, "row multi-slide counts two tiles moved");

const colState = [0, 1, 2, 3, 4, 5, 6, 7, 8];
const colSlide = sliderSlideToward(colState, 2, 3);
assert(colSlide?.state.join(",") === "0,1,8,3,4,2,6,7,5", "column multi-slide shifts tiles toward empty");
assert(colSlide?.tilesMoved === 2, "column multi-slide counts two tiles moved");

assert(sliderCanSlideToward(2, 8, 3), "same column can slide");
assert(!sliderCanSlideToward(1, 8, 3), "diagonal cannot slide");
assert(sliderSlideToward(rowState, 2, 3) === null, "empty position does nothing");

const winMsg = sliderPickWinMessage("hero", () => 0);
assert(winMsg?.title && winMsg?.body, "win message has title and body");
assert(winMsg.body.includes("Chittin"), "hero win message includes show name");

console.log(`Slider puzzle tests: ${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
