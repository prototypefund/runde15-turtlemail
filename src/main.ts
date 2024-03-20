import htmx from "htmx.org";

htmx.on("htmx:responseError", (e) => {
  console.error(e);
});
