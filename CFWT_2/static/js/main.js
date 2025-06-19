document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const sidebar = document.querySelector('.sidebar');
    const toggleButtons = document.querySelectorAll('.toggle-sidebar, .mobile-sidebar-toggle');
    const deleteModal = document.getElementById('deleteModal');
    
    // Toggle sidebar function
    const toggleSidebar = () => {
        if (window.innerWidth <= 1200) {
            sidebar.classList.toggle('visible');
        } else {
            sidebar.classList.toggle('collapsed');
            localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
        }
    };
    
    // Initialize sidebar state
    const loadSidebarState = () => {
        if (window.innerWidth > 1200) {
            const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
            if (isCollapsed) {
                sidebar.classList.add('collapsed');
            } else {
                sidebar.classList.remove('collapsed');
            }
        }
    };
    
    // Event listeners for all toggle buttons
    toggleButtons.forEach(button => {
        button.addEventListener('click', toggleSidebar);
    });
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 1200 && 
            !sidebar.contains(e.target) && 
            !Array.from(toggleButtons).some(btn => btn.contains(e.target))) {
            sidebar.classList.remove('visible');
        }
    });

    // Initialize Bootstrap collapse for submenus
    const collapses = document.querySelectorAll('.submenu');
    collapses.forEach(collapse => {
        new bootstrap.Collapse(collapse, {
            toggle: false
        });
    });

    // Keep active submenu open
    const activeSubmenuItem = document.querySelector('.submenu-item.active');
    if (activeSubmenuItem) {
        const submenu = activeSubmenuItem.closest('.submenu');
        if (submenu) {
            new bootstrap.Collapse(submenu, { toggle: false }).show();
        }
    }

    // Handle responsive behavior
    const handleResponsive = () => {
        if (window.innerWidth <= 1200) {
            sidebar.classList.remove('collapsed');
            sidebar.classList.remove('visible');
            document.querySelector('.mobile-sidebar-toggle').style.display = 'flex';
        } else {
            sidebar.classList.remove('visible');
            document.querySelector('.mobile-sidebar-toggle').style.display = 'none';
            loadSidebarState();
        }
    };
    
    // Initialize chart
    const initChart = () => {
        const ctx = document.getElementById('fundingChart');
        if (!ctx) return;
        
        new Chart(ctx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Funding Received ($)',
                    data: [12000000, 19000000, 3000000, 5000000, 2000000, 3000000],
                    backgroundColor: 'rgba(79, 70, 229, 0.7)',
                    borderColor: 'rgba(79, 70, 229, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return '$' + context.raw.toLocaleString();
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + (value / 1000000).toLocaleString() + 'M';
                            }
                        }
                    }
                }
            }
        });
    };
    
    // Delete modal handling
    if (deleteModal) {
        deleteModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const deleteUrl = button.getAttribute('data-delete-url');
            const form = deleteModal.querySelector('form');
            form.action = deleteUrl;
        });
        
        const deleteForm = document.getElementById('deleteForm');
        if (deleteForm) {
            deleteForm.addEventListener('submit', function(e) {
                const submitBtn = this.querySelector('button[type="submit"]');
                const deleteText = submitBtn.querySelector('.delete-text');
                const spinner = submitBtn.querySelector('.loading-spinner');
                
                deleteText.classList.add('d-none');
                spinner.classList.remove('d-none');
                submitBtn.disabled = true;
            });
        }
    }
    
    // Initialize
    handleResponsive();
    window.addEventListener('resize', handleResponsive);
    initChart();
});