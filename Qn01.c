#include <Arduino.h>

#define MAX_PLAYLIST_SIZE 10

// ==================== TYPE DEFINITIONS ====================

struct Song {
  char title[50];
  char artist[50];
  int duration; // in seconds
};

// --- Array-based Playlist Implementation ---

struct ArrayList {
  Song songs[MAX_PLAYLIST_SIZE];
  int size = 0;
};

struct SongNode {
  Song song;
  SongNode* next;
};

struct LinkedList {
  SongNode* head = nullptr;
};

// ==================== FUNCTION PROTOTYPES ====================

// Array list functions
void addSong(ArrayList* list, const Song& newSong);
void removeSong(ArrayList* list, int index);
void displayPlaylist(const ArrayList* list);

// Linked list functions
void addSong(LinkedList* list, const Song& newSong);
void removeSong(LinkedList* list, int index);
void displayPlaylist(const LinkedList* list);

// ===========================================================
// ================= ARRAY IMPLEMENTATION ====================
// ===========================================================

// TODO: Add a song to the end of the array list. Check for overflow.
void addSong(ArrayList* list, const Song& newSong) {

  // Check if array is already full
  if (list->size >= MAX_PLAYLIST_SIZE) {
    Serial.println("Array Overflow! Cannot add more songs.");
    return;
  }

  // Insert new song at current size index
  list->songs[list->size] = newSong;

  // Increase size after insertion
  list->size++;
}

// TODO: Remove a song at a given index (0-based). Shift elements left.
void removeSong(ArrayList* list, int index) {

  // Validate index range
  if (index < 0 || index >= list->size) {
    Serial.println("Invalid index for Array removal.");
    return;
  }

  // Shift all elements after index one position to the left
  for (int i = index; i < list->size - 1; i++) {
    list->songs[i] = list->songs[i + 1];
  }

  // Decrease size after removal
  list->size--;
}

// TODO: Print all songs in the list.
void displayPlaylist(const ArrayList* list) {

  Serial.println("\n--- Array Playlist ---");

  if (list->size == 0) {
    Serial.println("Playlist is empty.");
    return;
  }

  // Loop through array and print details
  for (int i = 0; i < list->size; i++) {
    Serial.print(i);
    Serial.print(". ");
    Serial.print(list->songs[i].title);
    Serial.print(" - ");
    Serial.print(list->songs[i].artist);
    Serial.print(" (");
    Serial.print(list->songs[i].duration);
    Serial.println(" sec)");
  }
}

// ===========================================================
// ============== LINKED LIST IMPLEMENTATION =================
// ===========================================================

// TODO: Add a song to the end of the linked list.
void addSong(LinkedList* list, const Song& newSong) {

  // Dynamically allocate new node
  SongNode* newNode = new SongNode;
  newNode->song = newSong;
  newNode->next = nullptr;

  // If list is empty, new node becomes head
  if (list->head == nullptr) {
    list->head = newNode;
    return;
  }

  // Otherwise, traverse to last node
  SongNode* current = list->head;
  while (current->next != nullptr) {
    current = current->next;
  }

  // Attach new node at the end
  current->next = newNode;
}

// TODO: Remove a song at a given index (0-based).
void removeSong(LinkedList* list, int index) {

  if (list->head == nullptr) {
    Serial.println("Linked list is empty.");
    return;
  }

  if (index < 0) {
    Serial.println("Invalid index.");
    return;
  }

  // If removing head node
  if (index == 0) {
    SongNode* temp = list->head;
    list->head = temp->next;
    delete temp;   // Free memory
    return;
  }

  // Traverse to node before target
  SongNode* current = list->head;
  for (int i = 0; current != nullptr && i < index - 1; i++) {
    current = current->next;
  }

  // If index out of bounds
  if (current == nullptr || current->next == nullptr) {
    Serial.println("Invalid index for Linked List removal.");
    return;
  }

  // Remove node by re-linking pointers
  SongNode* temp = current->next;
  current->next = temp->next;
  delete temp;   // Free memory
}

// TODO: Print all songs in the list.
void displayPlaylist(const LinkedList* list) {

  Serial.println("\n--- Linked List Playlist ---");

  if (list->head == nullptr) {
    Serial.println("Playlist is empty.");
    return;
  }

  SongNode* current = list->head;
  int index = 0;

  // Traverse until nullptr
  while (current != nullptr) {
    Serial.print(index++);
    Serial.print(". ");
    Serial.print(current->song.title);
    Serial.print(" - ");
    Serial.print(current->song.artist);
    Serial.print(" (");
    Serial.print(current->song.duration);
    Serial.println(" sec)");
    current = current->next;
  }
}

// ===========================================================
// ========================== SETUP ==========================
// ===========================================================

void setup() {

  Serial.begin(115200);
  while (!Serial);

  // ---------------- ARRAY TEST ----------------
  Serial.println("=== Testing Array Playlist ===");

  ArrayList myArrayPlaylist;

  addSong(&myArrayPlaylist, {"Song A1", "Artist 1", 180});
  addSong(&myArrayPlaylist, {"Song B2", "Artist 2", 240});
  addSong(&myArrayPlaylist, {"Song C3", "Artist 3", 200});

  displayPlaylist(&myArrayPlaylist);

  removeSong(&myArrayPlaylist, 1);
  Serial.println("After removing index 1:");
  displayPlaylist(&myArrayPlaylist);

  // ---------------- LINKED LIST TEST ----------------
  Serial.println("\n=== Testing Linked List Playlist ===");

  LinkedList myLinkedListPlaylist;

  addSong(&myLinkedListPlaylist, {"Song X1", "Artist X", 195});
  addSong(&myLinkedListPlaylist, {"Song Y2", "Artist Y", 225});
  addSong(&myLinkedListPlaylist, {"Song Z3", "Artist Z", 215});

  displayPlaylist(&myLinkedListPlaylist);

  removeSong(&myLinkedListPlaylist, 1);
  Serial.println("After removing index 1:");
  displayPlaylist(&myLinkedListPlaylist);

  // Cleanup linked list to avoid memory leak
  SongNode* current = myLinkedListPlaylist.head;
  while (current != nullptr) {
    SongNode* temp = current;
    current = current->next;
    delete temp;
  }
}

void loop() {}
