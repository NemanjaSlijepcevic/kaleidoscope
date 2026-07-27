import { updatePagination } from "./pagination.js";

document.addEventListener("DOMContentLoaded", function () {
    let currentSort = { column: null, order: "asc" };
    const form = document.getElementById('image-search-form');
    const authorSelect = document.getElementById("author-filter");
    const placeSelect = document.getElementById("place-filter");
    const yearSelect = document.getElementById("year-filter");
    // One pagination bar above the gallery and one below; every copy is kept in
    // sync rather than one being the "real" one.
    const paginationContainers = document.querySelectorAll(".js-pagination");
    const paginateSelects = document.querySelectorAll(".js-paginate-by");
    let showAllPages = false;
    const searchTextInput = document.querySelector('input[name="search-field"]');
    const resultContainer = document.getElementById("image-gallery");
    const categoryCheckboxes = document.querySelectorAll('input[name="category"]');
    const lightboxElement = document.getElementById("imageLightbox");
    const lightboxImage = document.getElementById("lightboxImage");
    const lightboxDescription = document.getElementById("lightboxDescription");
    const lightboxPrev = document.getElementById("lightboxPrev");
    const lightboxNext = document.getElementById("lightboxNext");
    const lightboxModal = lightboxElement && window.bootstrap
        ? new window.bootstrap.Modal(lightboxElement)
        : null;
    let currentImages = [];
    let currentIndex = 0;
    let lastPageState = { hasNext: false, currentPage: 1, totalPages: 1 };
    
    if (!form || !resultContainer || !authorSelect || !placeSelect || !yearSelect
        || !paginateSelects.length) {
        console.error("Missing required form elements!");
        return;
    }

    const pageSize = () => paginateSelects[0].value;

    document.querySelectorAll("th[data-sort]").forEach(header => {
        header.addEventListener("click", function () {
            const column = this.getAttribute("data-sort");
            if (currentSort.column === column) {
                currentSort.order = currentSort.order === "asc" ? "desc" : "asc";
            } else {
                currentSort.column = column;
                currentSort.order = "asc";
            }
            fetchAndRenderImages(1);
        });
    });

    authorSelect.addEventListener("change", function () {
        fetchAndRenderImages(1);
    });

    placeSelect.addEventListener("change", function () {
        fetchAndRenderImages(1);
    });

    yearSelect.addEventListener("change", function () {
        fetchAndRenderImages(1);
    });

    paginateSelects.forEach((select) => {
        select.addEventListener("change", function () {
            // Mirror the choice onto the other bar so they never disagree.
            paginateSelects.forEach((other) => { other.value = this.value; });
            showAllPages = false;
            fetchAndRenderImages(1);
        });
    });

    paginationContainers.forEach((container) => {
        container.addEventListener("click", function (event) {
            const showAllButton = event.target.closest(".js-show-all-pages");
            if (showAllButton) {
                event.preventDefault();
                showAllPages = true;
                renderPagination();
                return;
            }
            if (event.target.matches(".page-link")) {
                event.preventDefault();
                const page = parseInt(event.target.dataset.page);
                if (!isNaN(page)) {
                    fetchAndRenderImages(page);
                }
            }
        });
    });

    // Debounced: without this every keystroke fires a full gallery request.
    let searchTimer;
    searchTextInput.addEventListener("input", function () {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(() => fetchAndRenderImages(1), 300);
    });

    categoryCheckboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", function () {
            fetchAndRenderImages(1);
        });
    });

    function fetchAndRenderImages(page = 1) {
        showSpinner();
    
        const params = new URLSearchParams();
        params.set("page", page);
        params.set("paginate_by", pageSize());

        const searchText = searchTextInput.value.trim();
        if (searchText) {
            params.set("search-field", searchText);
        }

        if (authorSelect.value) {
            params.set("author", authorSelect.value);
        }

        if (placeSelect.value) {
            params.set("place", placeSelect.value);
        }

        if (yearSelect.value) {
            params.set("year", yearSelect.value);
        }

        categoryCheckboxes.forEach((checkbox) => {
            if (checkbox.checked) {
                params.append("category", checkbox.value);
            }
        });

        if (currentSort.column) {
            params.set("sort", currentSort.column);
            params.set("order", currentSort.order);
        }

        fetch(window.location.pathname + "?" + params.toString(), {
            headers: { "X-Requested-With": "XMLHttpRequest" }
        })
        .then(response => response.json())
        .then(data => {
            updateGallery(data.images, data.can_edit);
            lastPageState = {
                hasNext: data.has_next,
                currentPage: data.current_page,
                totalPages: data.total_pages
            };
            renderPagination();
        })
        .catch(error => console.error("Error fetching images:", error))
        .finally(() => hideSpinner());
    }

    // Kept separate from the fetch so the "..." button can re-render the bars
    // from the last known state without going back to the server.
    function renderPagination() {
        updatePagination(
            paginationContainers,
            lastPageState.hasNext,
            lastPageState.currentPage,
            lastPageState.totalPages,
            { showAll: showAllPages, paginateBy: pageSize() }
        );
    }

    function showSpinner() {
        document.getElementById("loading-spinner").classList.add("loading");
        document.getElementById("image-gallery").classList.add("loading");
    }

    function hideSpinner() {
        document.getElementById("loading-spinner").classList.remove("loading");
        document.getElementById("image-gallery").classList.remove("loading");
    }

    function updateGallery(images, can_edit) {
        currentImages = images;
        resultContainer.innerHTML = images.length
            ? images.map((image, index) =>
                `
                <div class="col">
                    <div class="card h-100">
                        ${image.thumbnail_url ? `<img src="${image.thumbnail_url}" class="card-img-top js-lightbox" alt="${image.title}" data-index="${index}" loading="lazy" decoding="async" width="360" height="360">` : ""}
                        <div class="card-body">
                            <h6 class="card-title">${can_edit ? `<a href="${image.detail_url}">${image.title}</a>` : image.title}</h6>
                            <p class="card-text mb-1">${image.authors.join(", ")}</p>
                            <p class="card-text text-muted mb-0">${[image.place, image.year].filter(Boolean).join(" ")}</p>
                        </div>
                    </div>
                </div>
            `).join('')
            : `<div class="col"><div class="alert alert-info mb-0">Слика није пронађена</div></div>`;
    }

    function showLightboxAt(index) {
        if (!currentImages.length || !lightboxModal || !lightboxImage) {
            return;
        }

        const normalizedIndex = (index + currentImages.length) % currentImages.length;
        const image = currentImages[normalizedIndex];
        if (!image || !image.image_url) {
            return;
        }

        currentIndex = normalizedIndex;
        lightboxImage.src = image.image_url;
        lightboxImage.alt = image.title || "";
        if (lightboxDescription) {
            const description = (image.description || "").trim();
            if (description) {
                lightboxDescription.textContent = description;
                lightboxDescription.style.display = "block";
            } else {
                lightboxDescription.textContent = "";
                lightboxDescription.style.display = "none";
            }
        }
        lightboxModal.show();
    }

    resultContainer.addEventListener("click", function (event) {
        const target = event.target;
        if (!target.classList.contains("js-lightbox") || !lightboxModal || !lightboxImage) {
            return;
        }
        const index = parseInt(target.dataset.index, 10);
        if (!Number.isNaN(index)) {
            showLightboxAt(index);
        }
    });

    if (lightboxPrev) {
        lightboxPrev.addEventListener("click", function () {
            showLightboxAt(currentIndex - 1);
        });
    }

    if (lightboxNext) {
        lightboxNext.addEventListener("click", function () {
            showLightboxAt(currentIndex + 1);
        });
    }

    if (lightboxElement) {
        lightboxElement.addEventListener("shown.bs.modal", function () {
            document.addEventListener("keydown", handleLightboxKeys);
        });

        lightboxElement.addEventListener("hidden.bs.modal", function () {
            document.removeEventListener("keydown", handleLightboxKeys);
        });
    }

    function handleLightboxKeys(event) {
        if (event.key === "ArrowLeft") {
            showLightboxAt(currentIndex - 1);
        } else if (event.key === "ArrowRight") {
            showLightboxAt(currentIndex + 1);
        }
    }
    
    fetchAndRenderImages();
});
