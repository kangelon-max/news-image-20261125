// THE WORLD IN ONE DAY — Wednesday 25 November 2026 (news-image-20261125)
//
// Entrypoint. The repository ships a pre-rendered entry.png (drawn by
// gen.py). This program validates that PNG rigorously — signature, the
// whole chunk stream with a CRC-32 check on every chunk, IHDR dimensions
// of exactly 1024x1024, the 1 MiB size gate, and no trailing bytes after
// IEND — then copies it into the output directory and writes a
// codepoint-sorted manifest.json with the file's sha256, reading the copy
// back to prove the hash survived the copy. No timestamps, randomness or
// environment-dependent values reach any output.

import { createHash } from "node:crypto";
import { copyFileSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const SOURCE = join(HERE, "entry.png");
const OUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const MAX_BYTES = 1048576; // 1 MiB gate
const WANT_W = 1024;
const WANT_H = 1024;
const SIG = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];

// CRC-32 with the PNG polynomial (0xEDB88320), table-driven.
const CRC_TABLE: number[] = (() => {
  const table: number[] = [];
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    table.push(c >>> 0);
  }
  return table;
})();

function crc32(buf: Buffer, from: number, to: number): number {
  let c = 0xffffffff;
  for (let i = from; i < to; i++) c = CRC_TABLE[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

function sha256(buf: Buffer): string {
  return createHash("sha256").update(buf).digest("hex");
}

function fail(msg: string): never {
  throw new Error("entry.png validation failed: " + msg);
}

interface PngReport {
  chunks: string[];
  idatBytes: number;
  bitDepth: number;
  colorType: number;
}

function validate(buf: Buffer): PngReport {
  if (buf.length === 0) fail("file is empty");
  if (buf.length > MAX_BYTES) {
    fail(`size ${buf.length} exceeds the 1 MiB gate (${MAX_BYTES})`);
  }
  if (buf.length < 8 || !SIG.every((b, i) => buf[i] === b)) {
    fail("missing PNG signature");
  }
  let off = 8;
  let seenIhdr = false;
  let seenIend = false;
  let idatBytes = 0;
  let bitDepth = 0;
  let colorType = 0;
  const chunks: string[] = [];
  while (off < buf.length) {
    if (off + 8 > buf.length) fail(`truncated chunk header at ${off}`);
    const len = buf.readUInt32BE(off);
    const type = buf.toString("ascii", off + 4, off + 8);
    if (!/^[A-Za-z]{4}$/.test(type)) {
      fail(`chunk type at ${off} is not four ASCII letters`);
    }
    const dataFrom = off + 8;
    const dataTo = dataFrom + len;
    if (dataTo + 4 > buf.length) fail(`chunk ${type} at ${off} overruns file`);
    const stored = buf.readUInt32BE(dataTo);
    const actual = crc32(buf, off + 4, dataTo);
    if (stored !== actual) {
      fail(`chunk ${type} at ${off} has a bad CRC-32`);
    }
    chunks.push(type);
    if (type === "IHDR") {
      if (seenIhdr) fail("duplicate IHDR chunk");
      if (off !== 8) fail("IHDR is not the first chunk");
      if (len !== 13) fail("IHDR length is not 13");
      const w = buf.readUInt32BE(dataFrom);
      const h = buf.readUInt32BE(dataFrom + 4);
      if (w !== WANT_W || h !== WANT_H) {
        fail(`IHDR dimensions ${w}x${h}, want ${WANT_W}x${WANT_H}`);
      }
      // The rest of IHDR: only the shapes this entry may take. 8-bit
      // channels, truecolour with or without alpha, standard compression
      // and filtering, no interlace — anything else is not our poster.
      bitDepth = buf[dataFrom + 8];
      colorType = buf[dataFrom + 9];
      const compression = buf[dataFrom + 10];
      const filter = buf[dataFrom + 11];
      const interlace = buf[dataFrom + 12];
      if (bitDepth !== 8) fail(`IHDR bit depth ${bitDepth}, want 8`);
      if (colorType !== 2 && colorType !== 6) {
        fail(`IHDR colour type ${colorType}, want 2 (RGB) or 6 (RGBA)`);
      }
      if (compression !== 0) fail(`IHDR compression ${compression}, want 0`);
      if (filter !== 0) fail(`IHDR filter method ${filter}, want 0`);
      if (interlace !== 0) fail(`IHDR interlace ${interlace}, want 0`);
      seenIhdr = true;
    } else if (type === "IDAT") {
      if (!seenIhdr) fail("IDAT appears before IHDR");
      idatBytes += len;
    } else if (type === "IEND") {
      if (len !== 0) fail("IEND chunk is not empty");
      seenIend = true;
      off = dataTo + 4;
      break;
    }
    off = dataTo + 4;
  }
  if (!seenIhdr) fail("no IHDR chunk");
  if (idatBytes === 0) fail("no IDAT data");
  if (!seenIend) fail("no IEND chunk");
  if (off !== buf.length) {
    fail(`${buf.length - off} trailing byte(s) after IEND`);
  }
  return { chunks, idatBytes, bitDepth, colorType };
}

function main(): void {
  const buf = readFileSync(SOURCE);
  const report = validate(buf);
  const digest = sha256(buf);
  mkdirSync(OUT_DIR, { recursive: true });
  const target = join(OUT_DIR, "entry.png");
  copyFileSync(SOURCE, target);
  const back = readFileSync(target);
  // Prove the copy two ways: byte-for-byte equality, then the hash.
  if (!back.equals(buf)) {
    fail("copied file differs byte-for-byte from the validated source");
  }
  if (sha256(back) !== digest) {
    fail("copied file's sha256 does not match the validated source");
  }
  const entries = [{ path: "entry.png", bytes: buf.length, sha256: digest }];
  entries.sort((a, b) => (a.path < b.path ? -1 : a.path > b.path ? 1 : 0));
  writeFileSync(join(OUT_DIR, "manifest.json"),
                JSON.stringify(entries, null, 2) + "\n");
  console.log(`entry.png valid: ${buf.length} bytes, sha256 ${digest}`);
  console.log(
    `png: ${report.chunks.length} chunks (${report.chunks.join(", ")}), ` +
    `${report.idatBytes} IDAT bytes, bit depth ${report.bitDepth}, ` +
    `colour type ${report.colorType}, all CRC-32 verified`);
  console.log(`copied to ${target}; read-back is byte-identical`);
}

main();
