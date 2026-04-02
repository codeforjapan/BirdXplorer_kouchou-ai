export const semanticTokens = {
  colors: {
    font: {
      primary: { value: "{colors.white}" },
      secondary: { value: "{colors.gray.200}" },
      disable: { value: "{colors.gray.500}" },
      white: { value: "{colors.white}" },
      link: { value: "{colors.blue.300}" },
      visited: { value: "{colors.purple.300}" },
      error: { value: "{colors.red.300}" },
      aiTalking: { value: "{colors.purple.200}" },
    },
    button: {
      primary: {
        default: { value: "{colors.gray.800}" },
        hover: { value: "{colors.gray.600}" },
        active: { value: "{colors.gray.900}" },
      },
      hover: { value: "rgba(0, 0, 0, 0.06)" },
      active: { value: "rgba(0, 0, 0, 0.08)" },
    },
    bg: {
      white: { value: "{colors.gray.900}" },
      secondary: { value: "{colors.gray.800}" },
      disable: { value: "{colors.gray.700}" },
      tooltip: { value: "{colors.gray.600}" },
      overlay: { value: "rgba(255, 255, 255, 0.12)" },
      error: { value: "{colors.red.900}" },
      public: { value: "{colors.green.900}" },
      limitedPublic: { value: "{colors.yellow.900}" },
      private: { value: "{colors.red.900}" },
      processing: { value: "{colors.purple.900}" },
    },
    border: {
      default: { value: "{colors.whiteAlpha.500}" },
      weak: { value: "{colors.whiteAlpha.300}" },
      public: { value: "{colors.green.400}" },
      limitedPublic: { value: "{colors.yellow.500}" },
      private: { value: "{colors.red.400}" },
    },
  },
};
