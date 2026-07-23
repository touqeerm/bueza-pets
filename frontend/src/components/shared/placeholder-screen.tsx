export function PlaceholderScreen({
  title,
  description,
}: {
  title: string;
  description?: string;
}) {
  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-2 px-6 text-center">
      <h1 className="text-2xl font-semibold">{title}</h1>
      {description ? (
        <p className="text-muted-foreground">{description}</p>
      ) : null}
    </main>
  );
}
