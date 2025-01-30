from collections import namedtuple
import logging
import typing

import littletable as db

from . import constants

logger = logging.getLogger(__name__)

interfaces_data = f"""\
id,interface
{constants.ADAFRUIT},adafruit
{constants.DFROBOT},dfrobot"""

interfaces = db.Table('interfaces')
interfaces.create_index('id', unique=True)
interfaces.create_index('interface', unique=True)
interfaces.csv_import(interfaces_data, transforms={'id': int})

device_type_data = f"""\
type,device
{constants.BUS},bus
{constants.MUX},mux
{constants.CHANNEL},channel
{constants.DEVICE},device
{constants.METER},meter
{constants.DETECTOR},detector"""

device_types = db.Table('device_types')
device_types.create_index('type', unique=True)
device_types.csv_import(device_type_data, transforms={'type': int})

capabilities_data = f"""\
id,capability
{constants.FOUR_CHANNEL},four_channel
{constants.EIGHT_CHANNEL},eight_channel
{constants.PRESSURE},pressure
{constants.TEMPERATURE},temperature
{constants.ALTITUDE},altitude
{constants.RELATIVE_HUMIDITY},relative_humidity
{constants.AMBIENT_LIGHT},ambient_light
{constants.LUX},lux
{constants.VISIBLE},visible
{constants.INFRARED},infrared
{constants.FULL_SPECTRUM},full_spectrum
{constants.CO2},co2
{constants.PRESSURE_MSL},pressure_msl"""

capabilities = db.Table('capabilities')
capabilities.create_index('id', unique=True)
capabilities.create_index('capability', unique=True)
capabilities.csv_import(capabilities_data, transforms={'id': int})

device_ids_data = f"""\
id,device_name
{constants.VIRTUAL_DEVICE},VIRTUAL
{constants.PCA9546A},PCA9546A
{constants.PCA9548A},PCA9548A
{constants.BMP390},BMP390
{constants.SHT41},SHT41
{constants.VEML7700},VEML7700
{constants.SCD41},SCD41
{constants.TSL2591},TSL2591"""

device_ids = db.Table('device_ids')
device_ids.create_index('id', unique=True)
device_ids.create_index('device_name', unique=True)
device_ids.csv_import(device_ids_data, transforms={'id': int})

links = db.Table('links')
links.create_index('node', unique=True)
links.create_index('parent')

nodes = db.Table('nodes')
nodes.create_index('uuid', unique=True)
nodes.create_index('kind')

multiplexer_attributes = db.Table('multiplexer_attributes')
multiplexer_attributes.create_index('uuid')
multiplexer_objects = db.Table('multiplexer_objects')
multiplexer_objects.create_index('uuid')
channels = db.Table('channels')
channels.create_index('uuid')
device_attributes = db.Table('device_attributes')
device_attributes.create_index('uuid')
device_objects = db.Table('device_objects')
device_objects.create_index('uuid')
meter_attributes = db.Table('meter_attributes')
meter_attributes.create_index('uuid')
meter_objects = db.Table('meter_objects')
meter_objects.create_index('uuid')

class NonUniqueRecordQuery(Exception):
    """Non Unique Query"""

Field = namedtuple('Field', 'found field')
Record = namedtuple('Record', 'found record')

class UniqueRecordByWhere:
    def __init__(self, table: db.Table[db.TableContent]):
        self._table = table

    def __call__(self, where: dict[str, typing.Any] = None, **kwargs) -> Record:
        clauses = dict()
        if where is not None:
            clauses = {**where, **kwargs}
        else:
            clauses = {**kwargs}
        rec = self._table.where(**clauses)
        match len(rec):
            case 0:
                return Record(False, None)
            case 1:
                return Record(True, rec[0])
            case _:
                msg = 'Table {} - clause: {} - returned non unique record'.format(
                        self._table.table_name, clauses)
                raise NonUniqueRecordQuery(msg)

class UniqueRecordFieldByWhere:
    def __init__(self, table: db.Table[db.TableContent]):
        self._table = table

    def __call__(self, field: str, where: dict[str, typing.Any] = None, **kwargs) -> Field:
        clauses = dict()
        if where is not None:
            clauses = {**where, **kwargs}
        else:
            clauses = {**kwargs}
        rec = self._table.where(**clauses)
        match len(rec):
            case 0:
                return Field(False, None)
            case 1:
                return Field(True, getattr(rec[0], field))
            case _:
                msg = 'Table {} - clause: {} - returned non unique record'.format(
                        self._table.table_name, clauses)
                raise NonUniqueRecordQuery(msg)

interfaces_selector   = UniqueRecordFieldByWhere(interfaces)
devicetypes_selector  = UniqueRecordFieldByWhere(device_types)
capabilities_selector = UniqueRecordFieldByWhere(capabilities)
deviceids_selector    = UniqueRecordFieldByWhere(device_ids)
