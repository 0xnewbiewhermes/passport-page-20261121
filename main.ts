import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
const dir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(dir, { recursive: true });
copyFileSync('./entry.png', join(dir, 'entry.png'));
