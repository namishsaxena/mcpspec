export interface FilterOptions {
  include?: string[];
  exclude?: string[];
}

export function filterItems<T extends { name: string }>(
  items: T[],
  options: FilterOptions,
): T[] {
  const { include, exclude } = options;

  // include takes precedence when set (even if empty)
  if (include !== undefined) {
    return items.filter((item) =>
      include.some((pattern) => matchGlob(item.name, pattern)),
    );
  }

  // exclude mode: remove items matching any exclude pattern
  if (exclude !== undefined && exclude.length > 0) {
    return items.filter(
      (item) =>
        !exclude.some((pattern) => matchGlob(item.name, pattern)),
    );
  }

  // no filters — return all items
  return items;
}

export function matchGlob(name: string, pattern: string): boolean {
  const regexStr = globToRegex(pattern);
  const regex = new RegExp(`^${regexStr}$`);
  return regex.test(name);
}

function globToRegex(pattern: string): string {
  let result = "";
  for (let i = 0; i < pattern.length; i++) {
    const char = pattern[i]!;
    switch (char) {
      case "*":
        result += ".*";
        break;
      case "?":
        result += ".";
        break;
      case ".":
      case "+":
      case "^":
      case "$":
      case "{":
      case "}":
      case "(":
      case ")":
      case "|":
      case "[":
      case "]":
      case "\\":
        result += `\\${char}`;
        break;
      default:
        result += char;
    }
  }
  return result;
}
