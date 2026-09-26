export interface SemanticMotionBinding {
  group: string;
  candidates: number[];
}

export interface SemanticActionMap {
  behaviorMotions: Record<string, SemanticMotionBinding>;
  affectExpressions: Record<string, string>;
}

export const HARU_ACTION_MAP: SemanticActionMap = {
  // ⚠️ 旧代码（勿删）：Haru 模型的 18 类语义动作映射（更换为 Lisette 前使用）
  // behaviorMotions: {
  //   nod: { group: 'TapBody', candidates: [1, 3] },
  //   invite: { group: 'TapBody', candidates: [21] },
  //   wave: { group: 'TapBody', candidates: [10] },
  //   reject: { group: 'TapBody', candidates: [2, 7] },
  //   think: { group: 'TapBody', candidates: [11, 12] },
  //   question: { group: 'TapBody', candidates: [18, 12] },
  //   explain: { group: 'TapBody', candidates: [22, 23] },
  //   recommend: { group: 'TapBody', candidates: [24] },
  //   summary: { group: 'TapBody', candidates: [26] },
  //   wait: { group: 'TapBody', candidates: [19] },
  //   remind: { group: 'TapBody', candidates: [20] },
  //   warn: { group: 'TapBody', candidates: [25] },
  //   thanks: { group: 'TapBody', candidates: [17, 9] },
  //   apology: { group: 'TapBody', candidates: [16, 17] },
  //   care: { group: 'TapBody', candidates: [5, 9] },
  //   celebrate: { group: 'TapBody', candidates: [6, 13] },
  //   surprise: { group: 'TapBody', candidates: [13, 14] },
  //   sad: { group: 'TapBody', candidates: [15, 8] }
  // },
  // 新代码（当前使用）：Lisette 模型的语义动作映射
  // Lisette TapBody 下标: 0=jump_ani 1=hello_ani 2=sad_idle 3=angry_idle 4=frenzy_idle 5=hand_fiddle_idle 6=happy_transition
  behaviorMotions: {
    nod: { group: 'TapBody', candidates: [6] },
    wave: { group: 'TapBody', candidates: [1] },
    celebrate: { group: 'TapBody', candidates: [0] },
    sad: { group: 'TapBody', candidates: [2] },
    warn: { group: 'TapBody', candidates: [3] },
    reject: { group: 'TapBody', candidates: [3] },
    surprise: { group: 'TapBody', candidates: [4] },
    think: { group: 'TapBody', candidates: [5] }
  },
  affectExpressions: {
    smile: 'F01',
    warm: 'F01',
    neutral: 'F01',
    curious: 'F04',
    serious: 'F02',
    sorry: 'F03',
    sad: 'F03',
    surprised: 'F04',
    excited: 'F04'
  }
};
