#include <Arduino.h>

#define MAX_MENU_DEPTH 10

// ================= MENU IDs =================
#define MENU_MAIN 0
#define MENU_SETTINGS 1
#define MENU_DISPLAY_SETTINGS 2
#define MENU_AUDIO_SETTINGS 3
#define MENU_BRIGHTNESS 4
#define MENU_CONTRAST 5

// =======================================================
// TODO: Implement array-based stack for integers
// =======================================================

class MenuStack {

private:
  int stack[MAX_MENU_DEPTH];
  int top;  // Index of top element (-1 when empty)

public:
  MenuStack() : top(-1) {}

  // TODO: Push a menu ID onto the stack. Check overflow.
  void push(int menuId) {

    if (top >= MAX_MENU_DEPTH - 1) {
      Serial.println("Stack Overflow!");
      return;
    }

    stack[++top] = menuId;  // Move top and store value
  }

  // TODO: Pop and return top menu ID. Return -1 if empty.
  int pop() {

    if (top < 0) {
      Serial.println("Stack Underflow!");
      return -1;
    }

    return stack[top--];  // Return then decrease top
  }

  // TODO: Peek top menu ID without removing it.
  int peek() {

    if (top < 0) {
      return -1;
    }

    return stack[top];
  }

  bool isEmpty() {
    return top == -1;
  }
};

// =======================================================

MenuStack navStack;
int currentMenu = MENU_MAIN;

// =======================================================
// TODO: Display menu based on menu ID
// =======================================================

void displayMenu(int menuId) {

  Serial.println("\n--- Menu ---");

  switch (menuId) {

    case MENU_MAIN:
      Serial.println("1. Main Menu");
      Serial.println("Enter 's' for Settings");
      break;

    case MENU_SETTINGS:
      Serial.println("2. Settings Menu");
      Serial.println("Enter 'd' for Display Settings");
      Serial.println("Enter 'a' for Audio Settings");
      Serial.println("Enter 'b' to go Back");
      break;

    case MENU_DISPLAY_SETTINGS:
      Serial.println("3. Display Settings Menu");
      Serial.println("Enter 'r' for Brightness");
      Serial.println("Enter 'c' for Contrast");
      Serial.println("Enter 'b' to go Back");
      break;

    case MENU_AUDIO_SETTINGS:
      Serial.println("3. Audio Settings Menu");
      Serial.println("(No sub-menus)");
      Serial.println("Enter 'b' to go Back");
      break;

    case MENU_BRIGHTNESS:
      Serial.println("4. Brightness Menu");
      Serial.println("Enter 'b' to go Back");
      break;

    case MENU_CONTRAST:
      Serial.println("5. Contrast Menu");
      Serial.println("Enter 'b' to go Back");
      break;

    default:
      Serial.println("Unknown Menu");
  }

  Serial.print("> ");
}

// =======================================================

void setup() {
  Serial.begin(115200);
  while (!Serial);

  displayMenu(currentMenu);
}

void loop() {

  if (Serial.available() > 0) {

    char command = Serial.read();

    // ================= BACK NAVIGATION =================
    if (command == 'b') {

      // TODO: If stack not empty, pop previous menu.
      // If empty, user is already at main menu.
      if (!navStack.isEmpty()) {
        currentMenu = navStack.pop();
      } else {
        Serial.println("Already at Main Menu.");
      }

    } 
    // ================= FORWARD NAVIGATION =================
    else {

      // TODO: Before navigating deeper,
      // push current menu onto stack
      navStack.push(currentMenu);

      // Change menu based on current state and command
      if (currentMenu == MENU_MAIN && command == 's') {
        currentMenu = MENU_SETTINGS;
      }
      else if (currentMenu == MENU_SETTINGS && command == 'd') {
        currentMenu = MENU_DISPLAY_SETTINGS;
      }
      else if (currentMenu == MENU_SETTINGS && command == 'a') {
        currentMenu = MENU_AUDIO_SETTINGS;
      }
      else if (currentMenu == MENU_DISPLAY_SETTINGS && command == 'r') {
        currentMenu = MENU_BRIGHTNESS;
      }
      else if (currentMenu == MENU_DISPLAY_SETTINGS && command == 'c') {
        currentMenu = MENU_CONTRAST;
      }
      else {
        // If invalid navigation, undo push
        navStack.pop();
        Serial.println("Invalid Option.");
      }
    }

    displayMenu(currentMenu);
  }
}
/*
ANALYSIS:
Stack implements LIFO.
Push and pop are O(1).
No dynamic memory used.
Ideal for back navigation systems.
Safe for embedded systems.
*/
