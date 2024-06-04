// (A) INITIALIZE - DOUBLE CLICK TO EDIT CELL
window.addEventListener("DOMContentLoaded", () => {
  for (let cell of document.querySelectorAll(".editable td")) {
    cell.ondblclick = () => editable.edit(cell);
  }
});
window.addEventListener('load', function() {
  // Get the viewport height and width
  const vh = window.innerHeight;
  const vw = window.innerWidth;

  // Get the body element
  const body = document.body;

  // Set the body dimensions to match the viewport
  body.style.width = vw  + 'px';
  body.style.height = vh + 'px';

  // Set the body font size based on viewport width
  // const fontSize = vw * 0.03; // Adjust the multiplier as needed
  // body.style.fontSize = fontSize + 'px';
});
var editable = {
  // (B) PROPERTIES
  selected : null,  // current selected cell
  value : "", // current selected cell value

  // (C) "CONVERT" TO EDITABLE CELL
  edit : cell => {
    // (C1) REMOVE "DOUBLE CLICK TO EDIT"
    cell.ondblclick = "";

    // (C2) EDITABLE CONTENT
    cell.contentEditable = true;
    cell.focus();

    // (C3) "MARK" CURRENT SELECTED CELL
    cell.classList.add("edit");
    editable.selected = cell;
    editable.value = cell.innerHTML;

    // (C4) PRESS ENTER/ESC OR CLICK OUTSIDE TO END EDIT
    window.addEventListener("click", editable.close);
    cell.onkeydown = evt => {
      if (evt.key=="Enter" || evt.key=="Escape") {
        editable.close(evt.key=="Enter" ? true : false);
        return false;
      }
    };
  },

  // (D) END "EDIT MODE"
  close : evt => { if (evt.target != editable.selected) {
    // (D1) CANCEL - RESTORE PREVIOUS VALUE
    if (evt === false) {
      editable.selected.innerHTML = editable.value;
    }

    // (D2) REMOVE "EDITABLE"
    window.getSelection().removeAllRanges();
    editable.selected.contentEditable = false;

    // (D3) RESTORE CLICK LISTENERS
    window.removeEventListener("click", editable.close);
    let cell = editable.selected;
    cell.onkeydown = "";
    cell.ondblclick = () => editable.edit(cell);

    // (D4) "UNMARK" CURRENT SELECTED CELL
    editable.selected.classList.remove("edit");
    editable.selected = null;
    editable.value = "";



    // (D5) DO WHATEVER YOU NEED
    if (evt !== false) {
      console.log(cell.innerHTML);
      // check value?
      // send value to server?
      // update calculations in table?
    }
  }}
};
