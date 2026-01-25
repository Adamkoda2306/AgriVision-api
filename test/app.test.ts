import request from 'supertest';
import app from "../app";


// ------------- DEFAULT CASE TESTING -------------------------
describe("API Tests", () => {
    it("Server Started", async () => {
        const res = await request(app).get('/');
        expect(res.statusCode).toBe(200);
        expect(res.body).toEqual({ message: "Server Started!"});
    });
});