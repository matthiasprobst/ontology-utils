from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class LanguageExtension:
    pass

class M4I(DefinedNamespace):
    # uri = "http://w3id.org/nfdi4ing/metadata4ing#"
    # Generated with ontolutils version 0.26.0
    # Date: 2025-12-21 09:04:43.610177
    _fail = True
    BooleanVariable: URIRef  # ['boolean variable']
    Method: URIRef  # ['method']
    NumericalAssignment: URIRef  # ['numerical assignment']
    NumericalVariable: URIRef  # ['numerical variable']
    ProcessingStep: URIRef  # ['processing step']
    Configuration: URIRef  # ['configuration']
    TextVariable: URIRef  # ['text variable']
    Tool: URIRef  # ['tool']
    VariableSet: URIRef  # ['variable set']
    configures: URIRef  # ['configures']
    hasAdmissibleValue: URIRef  # ['has admissible value']
    hasAssignedParameter: URIRef  # ['has assigned parameter']
    hasAssignedParameterSet: URIRef  # ['has assigned parameter set']
    hasAssignedValue: URIRef  # ['has assigned value']
    hasEmployedTool: URIRef  # ['has employed tool']
    hasFixedParameter: URIRef  # ['has fixed parameter']
    hasFixedParameterSet: URIRef  # ['has fixed parameter set']
    hasKindOfQuantity: URIRef  # ['has kind of quantity']
    hasParameter: URIRef  # ['has parameter']
    hasParameterSet: URIRef  # ['has parameter set']
    hasRuntimeAssignment: URIRef  # ['has runtime assignment']
    hasUncertaintyDeclaration: URIRef  # ['has uncertainty declaration']
    hasUnit: URIRef  # ['has unit']
    hasVariable: URIRef  # ['has variable']
    implementedByTool: URIRef  # ['implemented by']
    implementsMethod: URIRef  # ['implements']
    inProject: URIRef  # ['associated to project']
    investigates: URIRef  # ['investigates']
    investigatesProperty: URIRef  # ['investigates property']
    isEmployedToolIn: URIRef  # ['is employed tool']
    projectParticipant: URIRef  # ['project participant']
    realizesMethod: URIRef  # ['realizes method']
    representsVariable: URIRef  # ['represents variable']
    usesConfiguration: URIRef  # ['uses configuration']
    UsageInstruction: URIRef  # ['usage instruction']
    endOfProject: URIRef  # ['project end date']
    hasAssignmentTimestamp: URIRef  # ['has assignment timestamp']
    hasBooleanValue: URIRef  # ['has boolean value']
    hasDateAssignmentCreated: URIRef  # ['has date assignment created']
    hasDateAssignmentDeleted: URIRef  # ['has date assignment deleted']
    hasDateAssignmentModified: URIRef  # ['has date assignment modified']
    hasDateAssignmentValidFrom: URIRef  # ['has date assignment valid from']
    hasDateAssignmentValidUntil: URIRef  # ['has date assignment valid until']
    hasMaximumValue: URIRef  # ['has maximum value']
    hasMinimumValue: URIRef  # ['has minimum value']
    hasNumericalValue: URIRef  # ['has numerical value']
    hasRorId: URIRef  # ['has ROR ID']
    hasStepSize: URIRef  # ['has step size']
    hasStringValue: URIRef  # ['has string value']
    hasSymbol: URIRef  # ['has symbol']
    hasValue: URIRef  # ['has value']
    hasVariableDescription: URIRef  # ['has variable description']
    identifier: URIRef  # ['has identifier']
    orcidId: URIRef  # ['has ORCID ID']
    projectReferenceID: URIRef  # ['has project ID']
    startOfProject: URIRef  # ['project start date']
    ContactPerson: URIRef  # ['contact person']
    DataCollector: URIRef  # ['data collector']
    DataCurator: URIRef  # ['data curator']
    DataManager: URIRef  # ['data manager']
    Distributor: URIRef  # ['distributor']
    Editor: URIRef  # ['editor']
    HostingInstitution: URIRef  # ['hosting institution']
    Other: URIRef  # ['other person']
    Producer: URIRef  # ['producer']
    ProjectLeader: URIRef  # ['project leader']
    ProjectManager: URIRef  # ['project manager']
    ProjectMember: URIRef  # ['project member']
    RegistrationAgency: URIRef  # ['registration agency']
    RegistrationAuthority: URIRef  # ['registration authority']
    RelatedPerson: URIRef  # ['related person']
    ResearchGroup: URIRef  # ['research group']
    Researcher: URIRef  # ['researcher']
    RightsHolder: URIRef  # ['rights holder']
    Sponsor: URIRef  # ['sponsor']
    Supervisor: URIRef  # ['supervisor']
    WorkPackageLeader: URIRef  # ['work package leader']

    _NS = Namespace("http://w3id.org/nfdi4ing/metadata4ing#")

de = LanguageExtension()

setattr(M4I, "boolean_variable", M4I.BooleanVariable)
setattr(M4I, "method", M4I.Method)
setattr(M4I, "numerical_assignment", M4I.NumericalAssignment)
setattr(M4I, "numerical_variable", M4I.NumericalVariable)
setattr(M4I, "processing_step", M4I.ProcessingStep)
setattr(M4I, "configuration", M4I.Configuration)
setattr(M4I, "text_variable", M4I.TextVariable)
setattr(M4I, "tool", M4I.Tool)
setattr(M4I, "variable_set", M4I.VariableSet)
setattr(M4I, "configures", M4I.configures)
setattr(M4I, "has_admissible_value", M4I.hasAdmissibleValue)
setattr(M4I, "has_assigned_parameter", M4I.hasAssignedParameter)
setattr(M4I, "has_assigned_parameter_set", M4I.hasAssignedParameterSet)
setattr(M4I, "has_assigned_value", M4I.hasAssignedValue)
setattr(M4I, "has_employed_tool", M4I.hasEmployedTool)
setattr(M4I, "has_fixed_parameter", M4I.hasFixedParameter)
setattr(M4I, "has_fixed_parameter_set", M4I.hasFixedParameterSet)
setattr(M4I, "has_kind_of_quantity", M4I.hasKindOfQuantity)
setattr(M4I, "has_parameter", M4I.hasParameter)
setattr(M4I, "has_parameter_set", M4I.hasParameterSet)
setattr(M4I, "has_runtime_assignment", M4I.hasRuntimeAssignment)
setattr(M4I, "has_uncertainty_declaration", M4I.hasUncertaintyDeclaration)
setattr(M4I, "has_unit", M4I.hasUnit)
setattr(M4I, "has_variable", M4I.hasVariable)
setattr(M4I, "implemented_by", M4I.implementedByTool)
setattr(M4I, "implements", M4I.implementsMethod)
setattr(M4I, "associated_to_project", M4I.inProject)
setattr(M4I, "investigates", M4I.investigates)
setattr(M4I, "investigates_property", M4I.investigatesProperty)
setattr(M4I, "is_employed_tool", M4I.isEmployedToolIn)
setattr(M4I, "project_participant", M4I.projectParticipant)
setattr(M4I, "realizes_method", M4I.realizesMethod)
setattr(M4I, "represents_variable", M4I.representsVariable)
setattr(M4I, "uses_configuration", M4I.usesConfiguration)
setattr(M4I, "usage_instruction", M4I.UsageInstruction)
setattr(M4I, "project_end_date", M4I.endOfProject)
setattr(M4I, "has_assignment_timestamp", M4I.hasAssignmentTimestamp)
setattr(M4I, "has_boolean_value", M4I.hasBooleanValue)
setattr(M4I, "has_date_assignment_created", M4I.hasDateAssignmentCreated)
setattr(M4I, "has_date_assignment_deleted", M4I.hasDateAssignmentDeleted)
setattr(M4I, "has_date_assignment_modified", M4I.hasDateAssignmentModified)
setattr(M4I, "has_date_assignment_valid_from", M4I.hasDateAssignmentValidFrom)
setattr(M4I, "has_date_assignment_valid_until", M4I.hasDateAssignmentValidUntil)
setattr(M4I, "has_maximum_value", M4I.hasMaximumValue)
setattr(M4I, "has_minimum_value", M4I.hasMinimumValue)
setattr(M4I, "has_numerical_value", M4I.hasNumericalValue)
setattr(M4I, "has_ROR_ID", M4I.hasRorId)
setattr(M4I, "has_step_size", M4I.hasStepSize)
setattr(M4I, "has_string_value", M4I.hasStringValue)
setattr(M4I, "has_symbol", M4I.hasSymbol)
setattr(M4I, "has_value", M4I.hasValue)
setattr(M4I, "has_variable_description", M4I.hasVariableDescription)
setattr(M4I, "has_identifier", M4I.identifier)
setattr(M4I, "has_ORCID_ID", M4I.orcidId)
setattr(M4I, "has_project_ID", M4I.projectReferenceID)
setattr(M4I, "project_start_date", M4I.startOfProject)
setattr(M4I, "contact_person", M4I.ContactPerson)
setattr(M4I, "data_collector", M4I.DataCollector)
setattr(M4I, "data_curator", M4I.DataCurator)
setattr(M4I, "data_manager", M4I.DataManager)
setattr(M4I, "distributor", M4I.Distributor)
setattr(M4I, "editor", M4I.Editor)
setattr(M4I, "hosting_institution", M4I.HostingInstitution)
setattr(M4I, "other_person", M4I.Other)
setattr(M4I, "producer", M4I.Producer)
setattr(M4I, "project_leader", M4I.ProjectLeader)
setattr(M4I, "project_manager", M4I.ProjectManager)
setattr(M4I, "project_member", M4I.ProjectMember)
setattr(M4I, "registration_agency", M4I.RegistrationAgency)
setattr(M4I, "registration_authority", M4I.RegistrationAuthority)
setattr(M4I, "related_person", M4I.RelatedPerson)
setattr(M4I, "research_group", M4I.ResearchGroup)
setattr(M4I, "researcher", M4I.Researcher)
setattr(M4I, "rights_holder", M4I.RightsHolder)
setattr(M4I, "sponsor", M4I.Sponsor)
setattr(M4I, "supervisor", M4I.Supervisor)
setattr(M4I, "work_package_leader", M4I.WorkPackageLeader)

setattr(M4I, "de", de)