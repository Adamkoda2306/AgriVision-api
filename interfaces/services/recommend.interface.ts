
export interface ICrop {
    latitude: number,
    longitude: number,
    manual_data: {
        N: number,
        P: number,
        K: number,
        ph: number,
        "Temperature (°C)": number,
        "Humidity (%)": number,
        "Rainfall (mm)": number
    },
}