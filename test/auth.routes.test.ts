import requests from "supertest";
import app from "../app";

describe("Login Auth Route", () => {
    it("-> Creating", async () => {
        const res = (await requests(app).post('/auth/login')).body({
            phonenumber: "7842487664"
        });
        expect(res.statusCode).toBe(201);
        expect(res.body).toEqual({});
    });
    
    it("-> Login", async () => {
        const res = (await requests(app).post('/auth/login')).body({
            phonenumber: "7842487664"
        });
        expect(res.statusCode).toBe(200);
        expect(res.body).toEqual({});
    });
});