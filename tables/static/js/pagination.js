const pageItem = (page, label, active) => `
    <li class="page-item ${active ? "active" : ""}">
        <a class="page-link" href="#" data-page="${page}">${label}</a>
    </li>
`;

const ellipsis = () => `
    <li class="page-item">
        <button type="button" class="page-link js-show-all-pages">&hellip;</button>
    </li>
`;

/**
 * Render the page links into every pagination bar on the page.
 *
 * There is one bar above the gallery and one below it, so the markup is built
 * once and written to all of them: they always show the same state, and neither
 * copy owns ids that the other would duplicate. `showAll` lives in the caller
 * rather than on a container's dataset so expanding one bar expands both.
 */
export function updatePagination(containers, hasNext, currentPage, totalPages, options = {}) {
    const bars = Array.from(containers);
    const { showAll = false, paginateBy } = options;

    if (paginateBy === "all") {
        bars.forEach((bar) => { bar.innerHTML = ""; });
        return;
    }

    const items = [];
    const prevPage = currentPage > 1 ? currentPage - 1 : null;
    const nextPage = hasNext ? currentPage + 1 : null;

    if (prevPage) {
        items.push(pageItem(prevPage, "&lsaquo;", false));
    }

    items.push(pageItem(1, 1, currentPage === 1));

    if (showAll || totalPages <= 7) {
        for (let i = 2; i < totalPages; i++) {
            items.push(pageItem(i, i, i === currentPage));
        }
    } else {
        if (currentPage > 4) {
            items.push(ellipsis());
        }
        for (let i = Math.max(2, currentPage - 2); i <= Math.min(currentPage + 2, totalPages - 1); i++) {
            items.push(pageItem(i, i, i === currentPage));
        }
        if (currentPage < totalPages - 3) {
            items.push(ellipsis());
        }
    }

    if (totalPages > 1) {
        items.push(pageItem(totalPages, totalPages, currentPage === totalPages));
    }

    if (nextPage) {
        items.push(pageItem(nextPage, "&rsaquo;", false));
    }

    const html = items.join("");
    bars.forEach((bar) => { bar.innerHTML = html; });
}
