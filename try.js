// db.js
import pkg from 'pg';
const { Client } = pkg;

const client = new Client({
    user: 'postgres',
    host: '127.0.0.1',
    database: 'try',
    password: '0330',
    port: 5432,
});

async function main() {
    try {
        await client.connect();
        console.log('✅ Conectado a PostgreSQL');

        // Ejecutamos una consulta de prueba
        const res = await client.query('SELECT NOW() as fecha');
        console.log('🕒 Hora en la BD:', res.rows[0].fecha);

    } catch (err) {
        console.error('❌ Error al conectar:', err);
    } finally {
        await client.end();
        console.log('🔌 Conexión cerrada');
    }
}

main();
