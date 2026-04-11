import { useEffect, useState } from "react";

/**
 * localStorage에 값을 영속화하는 제네릭 상태 훅.
 *
 * 읽기는 useState의 lazy initializer 패턴을 사용해 첫 페인트에서
 * 올바른 값을 바로 렌더하며, flash of default value를 방지한다.
 * 쓰기는 useEffect에서 JSON.stringify로 동기화한다.
 *
 * CSR-only 프로젝트(Vite SPA)라 SSR 일관성 우려 없음.
 */
export function useStickyState<T>(
  key: string,
  initial: T,
): [T, (value: T) => void] {
  const [value, setValue] = useState<T>(() => {
    try {
      const raw =
        typeof window !== "undefined" ? window.localStorage.getItem(key) : null;
      if (raw == null) return initial;
      return JSON.parse(raw) as T;
    } catch {
      return initial;
    }
  });

  useEffect(() => {
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch {
      // quota exceeded / disabled — silently ignore
    }
  }, [key, value]);

  return [value, setValue];
}
