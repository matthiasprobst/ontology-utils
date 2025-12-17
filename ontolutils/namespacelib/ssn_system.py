from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class SSN_SYSTEM(DefinedNamespace):
    _fail = True
    inCondition = URIRef("http://www.w3.org/ns/ssn/systems/inCondition")
    Condition = URIRef("http://www.w3.org/ns/ssn/systems/Condition")
    hasSystemCapability = URIRef("http://www.w3.org/ns/ssn/systems/hasSystemCapability")
    SystemCapability = URIRef("http://www.w3.org/ns/ssn/systems/SystemCapability")
    hasSystemProperty = URIRef("http://www.w3.org/ns/ssn/systems/hasSystemProperty")
    SystemProperty = URIRef("http://www.w3.org/ns/ssn/systems/SystemProperty")
    MeasurementRange = URIRef("http://www.w3.org/ns/ssn/systems/MeasurementRange")
    ActuationRange = URIRef("http://www.w3.org/ns/ssn/systems/ActuationRange")
    Accuracy = URIRef("http://www.w3.org/ns/ssn/systems/Accuracy")
    DetectionLimit = URIRef("http://www.w3.org/ns/ssn/systems/DetectionLimit")
    Drift = URIRef("http://www.w3.org/ns/ssn/systems/Drift")
    Frequency = URIRef("http://www.w3.org/ns/ssn/systems/Frequency")
    Latency = URIRef("http://www.w3.org/ns/ssn/systems/Latency")
    Precision = URIRef("http://www.w3.org/ns/ssn/systems/Precision")
    Resolution = URIRef("http://www.w3.org/ns/ssn/systems/Resolution")
    ResponseTime = URIRef("http://www.w3.org/ns/ssn/systems/ResponseTime")
    Selectivity = URIRef("http://www.w3.org/ns/ssn/systems/Selectivity")
    Sensitivity = URIRef("http://www.w3.org/ns/ssn/systems/Sensitivity")
    hasOperatingRange = URIRef("http://www.w3.org/ns/ssn/systems/hasOperatingRange")
    OperatingRange = URIRef("http://www.w3.org/ns/ssn/systems/OperatingRange")
    hasOperatingProperty = URIRef("http://www.w3.org/ns/ssn/systems/hasOperatingProperty")
    OperatingProperty = URIRef("http://www.w3.org/ns/ssn/systems/OperatingProperty")
    MaintenanceSchedule = URIRef("http://www.w3.org/ns/ssn/systems/MaintenanceSchedule")
    OperatingPowerRange = URIRef("http://www.w3.org/ns/ssn/systems/OperatingPowerRange")
    hasSurvivalRange = URIRef("http://www.w3.org/ns/ssn/systems/hasSurvivalRange")
    SurvivalRange = URIRef("http://www.w3.org/ns/ssn/systems/SurvivalRange")
    hasSurvivalProperty = URIRef("http://www.w3.org/ns/ssn/systems/hasSurvivalProperty")
    SurvivalProperty = URIRef("http://www.w3.org/ns/ssn/systems/SurvivalProperty")
    SystemLifetime = URIRef("http://www.w3.org/ns/ssn/systems/SystemLifetime")
    BatteryLifetime = URIRef("http://www.w3.org/ns/ssn/systems/BatteryLifetime")
    qualityOfObservation = URIRef("http://www.w3.org/ns/ssn/systems/qualityOfObservation")

    _NS = Namespace("http://www.w3.org/ns/ssn/systems/")
