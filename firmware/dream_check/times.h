// frames both checkers draw: {scene (0 city, 1 home, 2 sky), t seconds}. compare.js reads this file too.
struct CheckFrame { int scene; float t; };
const CheckFrame FRAMES[] = {
  {0, 0.2f}, {0, 3.0f}, {0, 8.8f}, {0, 9.5f}, {0, 11.0f}, {0, 13.0f}, {0, 15.7f}, {0, 40.0f},
  {1, 0.3f}, {1, 1.1f}, {1, 3.9f}, {1, 4.9f}, {1, 6.0f},
  {2, 0.5f}, {2, 2.0f}, {2, 4.2f}, {2, 6.0f},
};
