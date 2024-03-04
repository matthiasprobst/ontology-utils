from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class LanguageExtension:
    pass

class PIVMETA(DefinedNamespace):
    # uri = "https://w3id.org/nfdi4ing/metadata4ing#"
    # Generated with namespacelib version 0.3.0
    # Date: 2024-03-02 13:35:41.244037
    _fail = True
    time: URIRef  # ['time']
    BackgroundImageGeneration: URIRef  # ['background image generation']
    BackgroundSubtractionMethod: URIRef  # ['background subtraction']
    CorrelationMethod: URIRef  # ['correlation method']
    DigitalCamera: URIRef  # ['Digital Camera']
    ImageDewarp: URIRef  # ['image dewarp']
    ImageFilter: URIRef  # ['image filter']
    ImageRotation: URIRef  # ['image rotation']
    ImageType: URIRef  # ['image type']
    InterrogationMethod: URIRef  # ['interrogation method']
    MaskGeneration: URIRef  # ['mask generation']
    Multigrid: URIRef  # ['multi grid']
    Multipass: URIRef  # ['multi pass']
    OutlierDetectionMethod: URIRef  # ['outlier detection method']
    OutlierReplacementScheme: URIRef  # ['outlier replacement scheme']
    PIVEvaluation: URIRef  # ['piv evaluation']
    PIVSoftware: URIRef  # ['Piv Software']
    PeakSearchMethod: URIRef  # ['peak search method']
    PivDistribution: URIRef  # ['piv distribution']
    PivImageDistribution: URIRef  # ['piv image distribution']
    PivMaskDistribution: URIRef  # ['piv mask distribution']
    PivPostProcessing: URIRef  # ['piv post processing']
    PivPreProcessing: URIRef  # ['piv pre processing']
    PivProcessingStep: URIRef  # ['piv processing step']
    PivResultDistribution: URIRef  # ['piv result distribution']
    Singlepass: URIRef  # ['single pass']
    hasStandardName: URIRef  # ['has standard name']
    pivImageType: URIRef  # ['piv image type']
    useOutlierReplacementScheme: URIRef  # ['uses outlier replacement scheme']
    filenamePattern: URIRef  # ['filename pattern']
    fnumber: URIRef  # ['fnumber']
    numberOfRecords: URIRef  # ['number of records']
    ExperimentalImage: URIRef  # ['experimental image']
    Interpolation: URIRef  # ['interpolation']
    LeftRightFlip: URIRef  # ['left right flip']
    ReEvaluateWithLargerSample: URIRef  # ['re-evaluate with larger sample']
    SplitImage: URIRef  # ['split image']
    SyntheticImage: URIRef  # ['synthetic image']
    TopBottomFlip: URIRef  # ['top bottom flip']
    TryLowerOrderPeaks: URIRef  # ['try lower order peaks']
    micro_piv: URIRef  # ['micro piv']
    piv: URIRef  # ['piv']
    piv_first_peak_correlation_coefficient: URIRef  # ['piv_first_peak_correlation_coefficient']
    ptv: URIRef  # ['ptv']
    piv_correlation_coefficient: URIRef  # ['piv_correlation_coefficient']
    piv_second_peak_correlation_coefficient: URIRef  # ['piv_second_peak_correlation_coefficient']
    piv_third_peak_correlation_coefficient: URIRef  # ['piv_third_peak_correlation_coefficient']
    first_peak_x_displacement: URIRef  # ['first_peak_x_displacement']
    first_peak_y_displacement: URIRef  # ['first_peak_y_displacement']
    piv_flag: URIRef  # ['piv_flag']
    image_particle_density: URIRef  # ['image_particle_density']
    image_density: URIRef  # ['image_density']
    image_particle_diameter: URIRef  # ['image_particle_diameter']
    piv_image_index: URIRef  # ['piv_image_index']
    inplane_velocity: URIRef  # ['inplane_velocity']
    laser_sheet_thickness: URIRef  # ['laser_sheet_thickness']
    laser_sheet_shape_factor: URIRef  # ['laser_sheet_shape_factor']
    mean_seeding_particle_size: URIRef  # ['mean_seeding_particle_size']
    number_of_particles: URIRef  # ['number_of_particles']
    laser_pulse_delay: URIRef  # ['laser_pulse_delay']
    saturated_pixel_number: URIRef  # ['saturated_pixel_number']
    second_peak_x_displacement: URIRef  # ['second_peak_x_displacement']
    second_peak_y_displacement: URIRef  # ['second_peak_y_displacement']
    seeding_material: URIRef  # ['seeding_material']
    standard_deviation_of_image_particle_diameter: URIRef  # ['standard_deviation_of_image_particle_diameter']
    third_peak_x_displacement: URIRef  # ['third_peak_x_displacement']
    third_peak_y_displacement: URIRef  # ['third_peak_y_displacement']
    relative_time: URIRef  # ['relative_time']
    velocity: URIRef  # ['velocity']
    displacement: URIRef  # ['displacement']
    x_final_interrogation_window_overlap_size: URIRef  # ['x_final_interrogation_window_overlap_size']
    x_final_interrogation_window_size: URIRef  # ['x_final_interrogation_window_size']
    x_initial_interrogation_window_size: URIRef  # ['x_initial_interrogation_window_size']
    x_pixel_coordinate: URIRef  # ['x_pixel_coordinate']
    y_final_interrogation_window_overlap_size: URIRef  # ['y_final_interrogation_window_overlap_size']
    y_final_interrogation_window_size: URIRef  # ['y_final_interrogation_window_size']
    y_initial_interrogation_window_size: URIRef  # ['y_initial_interrogation_window_size']
    y_pixel_coordinate: URIRef  # ['y_pixel_coordinate']
    pixel_origin: URIRef  # ['pixel_origin']
    coordinate: URIRef  # ['coordinate']
    signal_to_noise_ratio: URIRef  # ['signal_to_noise_ratio']
    least_square_residual_of_z_displacement_reconstruction: URIRef  # ['least_square_residual_of_z_displacement_reconstruction']
    piv_scaling_factor: URIRef  # ['piv_scaling_factor']
    image_filter_kernel_size: URIRef  # ['image_filter_kernel_size']
    ccd_width: URIRef  # ['ccd_width']
    ccd_height: URIRef  # ['ccd_height']
    focal_length: URIRef  # ['focal_length']
    sensor_pixel_width: URIRef  # ['sensor_pixel_width']
    sensor_pixel_height: URIRef  # ['sensor_pixel_height']
    sensor_pixel_width_fill_factor: URIRef  # ['sensor_pixel_width_fill_factor']
    sensor_pixel_height_fill_factor: URIRef  # ['sensor_pixel_height_fill_factor']
    image_bit_depth: URIRef  # ['image_bit_depth']

    _NS = Namespace("https://matthiasprobst.github.io/pivmeta#")

setattr(PIVMETA, "time", PIVMETA.time)
setattr(PIVMETA, "background_image_generation", PIVMETA.BackgroundImageGeneration)
setattr(PIVMETA, "background_subtraction", PIVMETA.BackgroundSubtractionMethod)
setattr(PIVMETA, "correlation_method", PIVMETA.CorrelationMethod)
setattr(PIVMETA, "Digital_Camera", PIVMETA.DigitalCamera)
setattr(PIVMETA, "image_dewarp", PIVMETA.ImageDewarp)
setattr(PIVMETA, "image_filter", PIVMETA.ImageFilter)
setattr(PIVMETA, "image_rotation", PIVMETA.ImageRotation)
setattr(PIVMETA, "image_type", PIVMETA.ImageType)
setattr(PIVMETA, "interrogation_method", PIVMETA.InterrogationMethod)
setattr(PIVMETA, "mask_generation", PIVMETA.MaskGeneration)
setattr(PIVMETA, "multi_grid", PIVMETA.Multigrid)
setattr(PIVMETA, "multi_pass", PIVMETA.Multipass)
setattr(PIVMETA, "outlier_detection_method", PIVMETA.OutlierDetectionMethod)
setattr(PIVMETA, "outlier_replacement_scheme", PIVMETA.OutlierReplacementScheme)
setattr(PIVMETA, "piv_evaluation", PIVMETA.PIVEvaluation)
setattr(PIVMETA, "Piv_Software", PIVMETA.PIVSoftware)
setattr(PIVMETA, "peak_search_method", PIVMETA.PeakSearchMethod)
setattr(PIVMETA, "piv_distribution", PIVMETA.PivDistribution)
setattr(PIVMETA, "piv_image_distribution", PIVMETA.PivImageDistribution)
setattr(PIVMETA, "piv_mask_distribution", PIVMETA.PivMaskDistribution)
setattr(PIVMETA, "piv_post_processing", PIVMETA.PivPostProcessing)
setattr(PIVMETA, "piv_pre_processing", PIVMETA.PivPreProcessing)
setattr(PIVMETA, "piv_processing_step", PIVMETA.PivProcessingStep)
setattr(PIVMETA, "piv_result_distribution", PIVMETA.PivResultDistribution)
setattr(PIVMETA, "single_pass", PIVMETA.Singlepass)
setattr(PIVMETA, "has_standard_name", PIVMETA.hasStandardName)
setattr(PIVMETA, "piv_image_type", PIVMETA.pivImageType)
setattr(PIVMETA, "uses_outlier_replacement_scheme", PIVMETA.useOutlierReplacementScheme)
setattr(PIVMETA, "filename_pattern", PIVMETA.filenamePattern)
setattr(PIVMETA, "fnumber", PIVMETA.fnumber)
setattr(PIVMETA, "number_of_records", PIVMETA.numberOfRecords)
setattr(PIVMETA, "experimental_image", PIVMETA.ExperimentalImage)
setattr(PIVMETA, "interpolation", PIVMETA.Interpolation)
setattr(PIVMETA, "left_right_flip", PIVMETA.LeftRightFlip)
setattr(PIVMETA, "re-evaluate_with_larger_sample", PIVMETA.ReEvaluateWithLargerSample)
setattr(PIVMETA, "split_image", PIVMETA.SplitImage)
setattr(PIVMETA, "synthetic_image", PIVMETA.SyntheticImage)
setattr(PIVMETA, "top_bottom_flip", PIVMETA.TopBottomFlip)
setattr(PIVMETA, "try_lower_order_peaks", PIVMETA.TryLowerOrderPeaks)
setattr(PIVMETA, "micro_piv", PIVMETA.micro_piv)
setattr(PIVMETA, "piv", PIVMETA.piv)
setattr(PIVMETA, "piv_first_peak_correlation_coefficient", PIVMETA.piv_first_peak_correlation_coefficient)
setattr(PIVMETA, "ptv", PIVMETA.ptv)
setattr(PIVMETA, "piv_correlation_coefficient", PIVMETA.piv_correlation_coefficient)
setattr(PIVMETA, "piv_second_peak_correlation_coefficient", PIVMETA.piv_second_peak_correlation_coefficient)
setattr(PIVMETA, "piv_third_peak_correlation_coefficient", PIVMETA.piv_third_peak_correlation_coefficient)
setattr(PIVMETA, "first_peak_x_displacement", PIVMETA.first_peak_x_displacement)
setattr(PIVMETA, "first_peak_y_displacement", PIVMETA.first_peak_y_displacement)
setattr(PIVMETA, "piv_flag", PIVMETA.piv_flag)
setattr(PIVMETA, "image_particle_density", PIVMETA.image_particle_density)
setattr(PIVMETA, "image_density", PIVMETA.image_density)
setattr(PIVMETA, "image_particle_diameter", PIVMETA.image_particle_diameter)
setattr(PIVMETA, "piv_image_index", PIVMETA.piv_image_index)
setattr(PIVMETA, "inplane_velocity", PIVMETA.inplane_velocity)
setattr(PIVMETA, "laser_sheet_thickness", PIVMETA.laser_sheet_thickness)
setattr(PIVMETA, "laser_sheet_shape_factor", PIVMETA.laser_sheet_shape_factor)
setattr(PIVMETA, "mean_seeding_particle_size", PIVMETA.mean_seeding_particle_size)
setattr(PIVMETA, "number_of_particles", PIVMETA.number_of_particles)
setattr(PIVMETA, "laser_pulse_delay", PIVMETA.laser_pulse_delay)
setattr(PIVMETA, "saturated_pixel_number", PIVMETA.saturated_pixel_number)
setattr(PIVMETA, "second_peak_x_displacement", PIVMETA.second_peak_x_displacement)
setattr(PIVMETA, "second_peak_y_displacement", PIVMETA.second_peak_y_displacement)
setattr(PIVMETA, "seeding_material", PIVMETA.seeding_material)
setattr(PIVMETA, "standard_deviation_of_image_particle_diameter", PIVMETA.standard_deviation_of_image_particle_diameter)
setattr(PIVMETA, "third_peak_x_displacement", PIVMETA.third_peak_x_displacement)
setattr(PIVMETA, "third_peak_y_displacement", PIVMETA.third_peak_y_displacement)
setattr(PIVMETA, "relative_time", PIVMETA.relative_time)
setattr(PIVMETA, "velocity", PIVMETA.velocity)
setattr(PIVMETA, "displacement", PIVMETA.displacement)
setattr(PIVMETA, "x_final_interrogation_window_overlap_size", PIVMETA.x_final_interrogation_window_overlap_size)
setattr(PIVMETA, "x_final_interrogation_window_size", PIVMETA.x_final_interrogation_window_size)
setattr(PIVMETA, "x_initial_interrogation_window_size", PIVMETA.x_initial_interrogation_window_size)
setattr(PIVMETA, "x_pixel_coordinate", PIVMETA.x_pixel_coordinate)
setattr(PIVMETA, "y_final_interrogation_window_overlap_size", PIVMETA.y_final_interrogation_window_overlap_size)
setattr(PIVMETA, "y_final_interrogation_window_size", PIVMETA.y_final_interrogation_window_size)
setattr(PIVMETA, "y_initial_interrogation_window_size", PIVMETA.y_initial_interrogation_window_size)
setattr(PIVMETA, "y_pixel_coordinate", PIVMETA.y_pixel_coordinate)
setattr(PIVMETA, "pixel_origin", PIVMETA.pixel_origin)
setattr(PIVMETA, "coordinate", PIVMETA.coordinate)
setattr(PIVMETA, "signal_to_noise_ratio", PIVMETA.signal_to_noise_ratio)
setattr(PIVMETA, "least_square_residual_of_z_displacement_reconstruction", PIVMETA.least_square_residual_of_z_displacement_reconstruction)
setattr(PIVMETA, "piv_scaling_factor", PIVMETA.piv_scaling_factor)
setattr(PIVMETA, "image_filter_kernel_size", PIVMETA.image_filter_kernel_size)
setattr(PIVMETA, "ccd_width", PIVMETA.ccd_width)
setattr(PIVMETA, "ccd_height", PIVMETA.ccd_height)
setattr(PIVMETA, "focal_length", PIVMETA.focal_length)
setattr(PIVMETA, "sensor_pixel_width", PIVMETA.sensor_pixel_width)
setattr(PIVMETA, "sensor_pixel_height", PIVMETA.sensor_pixel_height)
setattr(PIVMETA, "sensor_pixel_width_fill_factor", PIVMETA.sensor_pixel_width_fill_factor)
setattr(PIVMETA, "sensor_pixel_height_fill_factor", PIVMETA.sensor_pixel_height_fill_factor)
setattr(PIVMETA, "image_bit_depth", PIVMETA.image_bit_depth)