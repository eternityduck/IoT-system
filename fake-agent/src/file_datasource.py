from csv import DictReader
from datetime import datetime
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.aggregated_data import AggregatedData
from domain.parking import Parking
import config


class FileDatasource:
    accelerometer_filename: str
    gps_filename: str
    parking_filename: str
    def __init__(
        self,
        accelerometer_filename: str,
        gps_filename: str,
        parking_filename: str,
    ) -> None:
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename
        self.parking_filename = parking_filename

    def read(self, *args) -> AggregatedData:
        accel_reader = DictReader(args[0], delimiter=',')
        gps_reader = DictReader(args[1], delimiter=',')
        parking_reader = DictReader(args[2], delimiter=',')
        
        
        accel_data = [Accelerometer(
                int(row["x"]),
                int(row["y"]),
                int(row["z"]),
            ) for row in accel_reader]
        
        gps_data = [Gps(
                float(row["latitude"]),
                float(row["longitude"]),
            ) for row in gps_reader]
        
        parking_data = [Parking(
                int(row["empty_count"]),
                Gps(
                    float(row["latitude"]),
                    float(row["longitude"]),
                ),
            ) for row in parking_reader]

        agr_data = [AggregatedData(
            accel,
            gps if gps is not None else Gps(float(0), float(0)),
            parking if parking is not None else Parking(0, Gps(float(0), float(0))),
            datetime.now(),
            config.USER_ID,
        ) for accel, gps, parking in zip(accel_data, gps_data + [None] * (len(accel_data) - len(gps_data)), parking_data + [None] * (len(accel_data) - len(parking_data)))]

        return agr_data

    def startReading(self, *args, **kwargs):
        accelometer = open(self.accelerometer_filename, 'r')
        gps = open(self.gps_filename, 'r')
        parking = open(self.parking_filename, 'r')
        print("Successfully opened files")
        return accelometer, gps, parking

    def stopReading(self, *args, **kwargs):
        for filename in args:
            print("Closing file...", filename.name)
            filename.close()
        
