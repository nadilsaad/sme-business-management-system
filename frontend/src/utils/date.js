export const formatDate = (value) =>
  value ? new Intl.DateTimeFormat("en-TZ", { dateStyle: "medium" }).format(new Date(value)) : "-";
