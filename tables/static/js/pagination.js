export function updatePagination(paginationContainer, hasNext, currentPage, totalPages) { 
    paginationContainer.innerHTML = "";

    if (document.getElementById("paginateBy").value === "all") return;

    const prevPage = currentPage > 1 ? currentPage - 1 : null;
    const nextPage = hasNext ? currentPage + 1 : null;
    const showAllButtonId = "showAllPages"; 
    const showAll = paginationContainer.dataset.showAll === "true";

    if (prevPage) {
        paginationContainer.innerHTML += `
            <li class="page-item">
                <a class="page-link" href="#" data-page="${prevPage}">&lsaquo;</a>
            </li>
        `;
    }

    paginationContainer.innerHTML += `
        <li class="page-item ${currentPage === 1 ? "active" : ""}">
            <a class="page-link" href="#" data-page="1">1</a>
        </li>
    `;

    if (showAll || totalPages <= 7) {
        for (let i = 2; i < totalPages; i++) {
            paginationContainer.innerHTML += `
                <li class="page-item ${i === currentPage ? "active" : ""}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `;
        }
    } else {
        if (currentPage > 4) {
            paginationContainer.innerHTML += `<li class="page-item"><button id="${showAllButtonId}" class="page-link">...</button></li>`;
        }

        for (let i = Math.max(2, currentPage - 2); i <= Math.min(currentPage + 2, totalPages - 1); i++) {
            paginationContainer.innerHTML += `
                <li class="page-item ${i === currentPage ? "active" : ""}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `;
        }

        if (currentPage < totalPages - 3) {
            paginationContainer.innerHTML += `<li class="page-item"><button id="${showAllButtonId}" class="page-link">...</button></li>`;
        }
    }

    if (totalPages > 1) {
        paginationContainer.innerHTML += `
            <li class="page-item ${currentPage === totalPages ? "active" : ""}">
                <a class="page-link" href="#" data-page="${totalPages}">${totalPages}</a>
            </li>
        `;
    }

    if (nextPage) {
        paginationContainer.innerHTML += `
            <li class="page-item">
                <a class="page-link" href="#" data-page="${nextPage}">&rsaquo;</a>
            </li>
        `;
    }

    setTimeout(() => {
        const showAllButton = document.getElementById(showAllButtonId);
        if (showAllButton) {
            showAllButton.addEventListener("click", () => {
                paginationContainer.dataset.showAll = "true";
                updatePagination(paginationContainer, hasNext, currentPage, totalPages);
            });
        }
    }, 0);
}
