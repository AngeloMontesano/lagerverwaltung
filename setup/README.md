# Setup-Hinweise

Im Ordner `setup/templates` liegt die vollständige Schema-Datei für MariaDB:

- `setup/templates/schema.sql`

Das Setup-Skript `setup/setup_lagerverwaltung.sh` kopiert diese Datei beim Anlegen einer neuen Kundeninstanz automatisch in das Kundenverzeichnis. Du kannst sie auch manuell ausführen, z. B. mit `mysql -u root -p < setup/templates/schema.sql`, um eine leere Datenbank mit allen Tabellen anzulegen.
