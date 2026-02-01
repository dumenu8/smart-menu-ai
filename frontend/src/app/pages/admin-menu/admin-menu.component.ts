import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MenuService, MenuItem } from '../../services/menu.service';

@Component({
    selector: 'app-admin-menu',
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule],
    templateUrl: './admin-menu.component.html',
    styleUrls: ['./admin-menu.component.scss']
})
export class AdminMenuComponent {
    private menuService = inject(MenuService);
    private fb = inject(FormBuilder);

    menuItems = signal<MenuItem[]>([]);
    itemForm: FormGroup;
    showForm = signal(false);
    editingId = signal<string | null>(null);

    constructor() {
        this.itemForm = this.fb.group({
            name: ['', Validators.required],
            description: ['', Validators.required],
            price: [0, [Validators.required, Validators.min(0)]],
            category: [''],
            image_data: [''] // We'll handle file upload separately to convert to base64
        });

        this.loadMenu();
    }

    loadMenu() {
        this.menuService.getMenuItems().subscribe(items => {
            this.menuItems.set(items);
        });
    }

    toggleForm() {
        this.editingId.set(null); // Ensure we are in Add mode
        this.showForm.update(v => !v);
        if (this.showForm()) {
            this.itemForm.reset();
            this.itemForm.patchValue({ price: 0, category: '' }); // Defaults
        }
    }

    cancelEdit() {
        this.editingId.set(null);
        this.resetForm();
    }

    onFileSelected(event: any) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e: any) => {
                this.itemForm.patchValue({ image_data: e.target.result });
            };
            reader.readAsDataURL(file);
        }
    }

    onSubmit() {
        if (this.itemForm.valid) {
            const formData = this.itemForm.value;
            const currentId = this.editingId();

            if (currentId) {
                this.menuService.updateMenuItem(currentId, formData).subscribe(updatedItem => {
                    this.menuItems.update(items => items.map(i => i.id === currentId ? updatedItem : i));
                    this.editingId.set(null); // Close inline edit
                });
            } else {
                this.menuService.createMenuItem(formData).subscribe(newItem => {
                    this.menuItems.update(items => [...items, newItem]);
                    this.resetForm(); // Close add form
                });
            }
        }
    }

    resetForm() {
        this.itemForm.reset();
        this.showForm.set(false);
        this.editingId.set(null);
    }

    editItem(item: MenuItem) {
        if (!item.id) return;
        this.showForm.set(false); // Hide top form
        this.editingId.set(item.id);
        this.itemForm.patchValue({
            name: item.name,
            description: item.description,
            price: item.price,
            category: item.category,
            image_data: item.image_data
        });
    }

    deleteItem(id: string | undefined) {
        if (!id) return;
        if (confirm('Are you sure you want to delete this item?')) {
            this.menuService.deleteMenuItem(id).subscribe(() => {
                this.menuItems.update(items => items.filter(i => i.id !== id));
            });
        }
    }
}
