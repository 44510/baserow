export const DIRECTIONS = {
  UP: 'up',
  DOWN: 'down',
  LEFT: 'left',
  RIGHT: 'right',
}

export const PLACEMENTS = {
  BEFORE: 'before',
  AFTER: 'after',
}
export const PAGE_PARAM_TYPE_VALIDATION_FUNCTIONS = {
  numeric: (value) => !isNaN(value),
  text: () => true, // Everything starts as text
}

export const IMAGE_SOURCE_TYPES = {
  UPLOAD: 'upload',
  URL: 'url',
}

export const ALIGNMENTS = {
  LEFT: {
    name: 'alignmentSelector.alignmentLeft',
    value: 'left',
    icon: 'align-left',
  },
  CENTER: {
    name: 'alignmentSelector.alignmentCenter',
    value: 'center',
    icon: 'align-center',
  },
  RIGHT: {
    name: 'alignmentSelector.alignmentRight',
    value: 'right',
    icon: 'align-right',
  },
}
