import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-selectable-list',
  templateUrl: './selectable-list.component.html',
  styleUrls: ['./selectable-list.component.scss']
})
export class SelectableListComponent implements OnInit {
  @Input() items: string[] = [];
  @Input() multiselect = true;
  @Input() selectedItems: string[] = [];
  @Output() selectionChange = new EventEmitter<string[]>();

  constructor() { }

  ngOnInit() { }

  toggleSelection(item: string) {
    const index = this.selectedItems.indexOf(item);
    if (index === -1) {
      if (!this.multiselect) {
        this.clearSelection();
      }

      this.selectedItems.push(item);
    } else if (this.multiselect) {
      this.selectedItems.splice(index, 1);
    }

    this.selectionChange.emit(this.selectedItems);
  }

  private clearSelection() {
    this.selectedItems.splice(0, this.selectedItems.length);
  }
}
