window.addEventListener("load", () => {
    setTimeout(() => {
        window.scrollTo({ top: 0, behavior: "instant" });
    }, 10); // slight delay to override iframe/focus-induced scroll
});
