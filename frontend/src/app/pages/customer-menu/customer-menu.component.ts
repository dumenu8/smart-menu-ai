import { Component, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MenuService, MenuItem } from '../../services/menu.service';


@Component({
    selector: 'app-customer-menu',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './customer-menu.component.html',
    styleUrls: ['./customer-menu.component.scss']
})
export class CustomerMenuComponent {
    private menuService = inject(MenuService);
    menuItems = signal<MenuItem[]>([]);
    categories = signal<string[]>([]);
    activeCategory = signal<string>('All');
    isLoading = signal(true);

    constructor() {
        this.menuService.getMenuItems().subscribe({
            next: (items) => {
                this.menuItems.set(items);
                this.extractCategories(items);
                this.isLoading.set(false);
            },
            error: () => this.isLoading.set(false)
        });
    }

    extractCategories(items: MenuItem[]) {
        const cats = new Set(items.map(i => i.category || 'General'));
        this.categories.set(['All', ...Array.from(cats)]);
    }

    filter(category: string) {
        this.activeCategory.set(category);
    }

    get filteredItems() {
        if (this.activeCategory() === 'All') return this.menuItems();
        return this.menuItems().filter(i => (i.category || 'General') === this.activeCategory());
    }
}
