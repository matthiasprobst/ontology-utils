from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class LanguageExtension:
    pass

class PIVMETA(DefinedNamespace):
    # uri = "https://w3id.org/nfdi4ing/metadata4ing#"
    # Generated with None version 0.2.16
    # Date: 2024-04-08 15:01:29.767768
    _fail = True
    time: URIRef  # ['time']
    BackgroundImageGeneration: URIRef  # ['background image generation']
    BackgroundSubtractionMethod: URIRef  # ['background subtraction']
    CorrelationMethod: URIRef  # ['Correlation Method']
    DigitalCamera: URIRef  # ['Digital Camera']
    DigitalCameraModel: URIRef  # ['Digital Camera Model']
    ImageDewarp: URIRef  # ['image dewarp']
    ImageFilter: URIRef  # ['image filter']
    ImageManipulationMethod: URIRef  # ['Image Manipulation Method']
    ImageRotation: URIRef  # ['image rotation']
    ImageType: URIRef  # ['Image Type']
    InterrogationMethod: URIRef  # ['Interrogation Method']
    LaserModel: URIRef  # ['Laser Model']
    MaskGeneration: URIRef  # ['mask generation']
    Multigrid: URIRef  # ['Multigrid']
    Multipass: URIRef  # ['Multipass']
    OutlierDetectionMethod: URIRef  # ['Outlier Detection Method']
    OutlierReplacementScheme: URIRef  # ['Outlier Replacement Scheme']
    PIVEvaluation: URIRef  # ['piv evaluation']
    PIVHardware: URIRef  # ['PIV Hardware']
    PIVSoftware: URIRef  # ['Piv Software']
    Particle: URIRef  # ['Particle']
    PeakSearchMethod: URIRef  # ['Peak Search Method']
    PivDistribution: URIRef  # ['piv distribution']
    PivImageDistribution: URIRef  # ['piv image distribution']
    PivMaskDistribution: URIRef  # ['piv mask distribution']
    PivPostProcessing: URIRef  # ['piv post processing']
    PivPreProcessing: URIRef  # ['piv pre processing']
    PivProcessingStep: URIRef  # ['piv processing step']
    PivResultDistribution: URIRef  # ['piv result distribution']
    PivType: URIRef  # ['PIV Type']
    PivValidation: URIRef  # ['piv validation']
    Singlepass: URIRef  # ['Singlepass']
    SyntheticParticle: URIRef  # ['Synthetic Particle']
    WindowWeightingFunction: URIRef  # ['Window Weighting Function']
    hasStandardName: URIRef  # ['has standard name']
    outlierReplacementScheme: URIRef  # ['outlier replacement scheme']
    pivImageType: URIRef  # ['piv image type']
    windowWeightingFunction: URIRef  # ['window weighting function']
    filenamePattern: URIRef  # ['filename pattern']
    flagMeanings: URIRef  # ['flag meanings']
    flagValues: URIRef  # ['flag values']
    fnumber: URIRef  # ['fnumber']
    material: URIRef  # ['material']
    numberOfRecords: URIRef  # ['number of records']
    ExperimentalImage: URIRef  # ['experimental image']
    GaussianWindow: URIRef  # ['Gaussian Window']
    HammingWindow: URIRef  # ['Hamming Window']
    HannWindow: URIRef  # ['Hann Window']
    Interpolation: URIRef  # ['Interpolation']
    LeftRightFlip: URIRef  # ['left right flip']
    MilliM_PER_PIXEL = URIRef("https://matthiasprobst.github.io/pivmeta#MilliM-PER-PIXEL")  # ['millimetre per pixel']
    PER_PIXEL = URIRef("https://matthiasprobst.github.io/pivmeta#PER-PIXEL")  # ['per pixel']
    ParticleImageVelocimetry: URIRef  # ['Particle Image Velocimetry']
    ParticleTrackingVelocimetry: URIRef  # ['Particle Tracking Velocimetry']
    ReEvaluateWithLargerSample: URIRef  # ['re-evaluate with larger sample']
    SpatialResolution: URIRef  # ['spatial resolution']
    SplitImage: URIRef  # ['split image']
    SquareWindow: URIRef  # ['Square Window']
    SyntheticImage: URIRef  # ['synthetic image']
    TopBottomFlip: URIRef  # ['top bottom flip']
    TryLowerOrderPeaks: URIRef  # ['try lower order peaks']
    TukeyWindow: URIRef  # ['Tukey Window']
    microPIV: URIRef  # ['Micro PIV']
    piv_first_peak_correlation_coefficient: URIRef  # ['piv_first_peak_correlation_coefficient']
    piv_correlation_coefficient: URIRef  # ['piv_correlation_coefficient']
    piv_second_peak_correlation_coefficient: URIRef  # ['piv_second_peak_correlation_coefficient']
    piv_third_peak_correlation_coefficient: URIRef  # ['piv_third_peak_correlation_coefficient']
    first_peak_x_displacement: URIRef  # ['first_peak_x_displacement']
    first_peak_y_displacement: URIRef  # ['first_peak_y_displacement']
    x_derivative_of_x_velocity: URIRef  # ['x_derivative_of_x_velocity']
    x_derivative_of_y_velocity: URIRef  # ['x_derivative_of_y_velocity']
    y_derivative_of_x_velocity: URIRef  # ['y_derivative_of_x_velocity']
    y_derivative_of_y_velocity: URIRef  # ['y_derivative_of_y_velocity']
    x_derivative_of_z_velocity: URIRef  # ['x_derivative_of_z_velocity']
    y_derivative_of_z_velocity: URIRef  # ['y_derivative_of_z_velocity']
    z_derivative_of_x_velocity: URIRef  # ['z_derivative_of_x_velocity']
    piv_flag: URIRef  # ['piv_flag']
    image_particle_density: URIRef  # ['image_particle_density']
    image_density: URIRef  # ['image_density']
    image_particle_diameter: URIRef  # ['image_particle_diameter']
    arithmetic_mean_of_image_particle_diameter: URIRef  # ['arithmetic_mean_of_image_particle_diameter']
    standard_deviation_of_image_particle_diameter: URIRef  # ['standard_deviation_of_image_particle_diameter']
    image_index: URIRef  # ['image_index']
    inplane_velocity: URIRef  # ['inplane_velocity']
    x_inplane_velocity: URIRef  # ['x_inplane_velocity']
    y_inplane_velocity: URIRef  # ['y_inplane_velocity']
    model_laser_sheet_thickness: URIRef  # ['model_laser_sheet_thickness']
    laser_sheet_thickness: URIRef  # ['laser_sheet_thickness']
    model_laser_sheet_shape_factor: URIRef  # ['model_laser_sheet_shape_factor']
    arithmetic_mean_of_seeding_particle_size: URIRef  # ['arithmetic_mean_of_seeding_particle_size']
    standard_deviation_of_seeding_particle_size: URIRef  # ['standard_deviation_of_seeding_particle_size']
    number_of_particles: URIRef  # ['number_of_particles']
    saturated_pixel_number: URIRef  # ['saturated_pixel_number']
    second_peak_x_displacement: URIRef  # ['second_peak_x_displacement']
    second_peak_y_displacement: URIRef  # ['second_peak_y_displacement']
    third_peak_x_displacement: URIRef  # ['third_peak_x_displacement']
    third_peak_y_displacement: URIRef  # ['third_peak_y_displacement']
    relative_time: URIRef  # ['relative_time']
    magnitude_of_velocity: URIRef  # ['magnitude_of_velocity']
    x_velocity: URIRef  # ['x_velocity']
    y_velocity: URIRef  # ['y_velocity']
    z_velocity: URIRef  # ['z_velocity']
    displacement: URIRef  # ['displacement']
    x_displacement: URIRef  # ['x_displacement']
    y_displacement: URIRef  # ['y_displacement']
    final_interrogation_window_overlap_size: URIRef  # ['final_interrogation_window_overlap_size']
    x_final_interrogation_window_overlap_size: URIRef  # ['x_final_interrogation_window_overlap_size']
    final_interrogation_window_size: URIRef  # ['final_interrogation_window_size']
    x_final_interrogation_window_size: URIRef  # ['x_final_interrogation_window_size']
    initial_interrogation_window_size: URIRef  # ['initial_interrogation_window_size']
    x_initial_interrogation_window_size: URIRef  # ['x_initial_interrogation_window_size']
    x_pixel_coordinate: URIRef  # ['x_pixel_coordinate']
    y_final_interrogation_window_overlap_size: URIRef  # ['y_final_interrogation_window_overlap_size']
    y_final_interrogation_window_size: URIRef  # ['y_final_interrogation_window_size']
    y_initial_interrogation_window_size: URIRef  # ['y_initial_interrogation_window_size']
    y_pixel_coordinate: URIRef  # ['y_pixel_coordinate']
    x_image_coordinate: URIRef  # ['x_image_coordinate']
    x_origin_offset: URIRef  # ['x_origin_offset']
    y_image_coordinate: URIRef  # ['y_image_coordinate']
    y_origin_offset: URIRef  # ['y_origin_offset']
    x_coordinate: URIRef  # ['x_coordinate']
    y_coordinate: URIRef  # ['y_coordinate']
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
    optical_magnification: URIRef  # ['optical_magnification']
    laser_pulse_delay: URIRef  # ['laser_pulse_delay']

    _NS = Namespace("https://matthiasprobst.github.io/pivmeta#")

setattr(PIVMETA, "time", PIVMETA.time)
setattr(PIVMETA, "background_image_generation", PIVMETA.BackgroundImageGeneration)
setattr(PIVMETA, "background_subtraction", PIVMETA.BackgroundSubtractionMethod)
setattr(PIVMETA, "Correlation_Method", PIVMETA.CorrelationMethod)
setattr(PIVMETA, "Digital_Camera", PIVMETA.DigitalCamera)
setattr(PIVMETA, "Digital_Camera_Model", PIVMETA.DigitalCameraModel)
setattr(PIVMETA, "image_dewarp", PIVMETA.ImageDewarp)
setattr(PIVMETA, "image_filter", PIVMETA.ImageFilter)
setattr(PIVMETA, "Image_Manipulation_Method", PIVMETA.ImageManipulationMethod)
setattr(PIVMETA, "image_rotation", PIVMETA.ImageRotation)
setattr(PIVMETA, "Image_Type", PIVMETA.ImageType)
setattr(PIVMETA, "Interrogation_Method", PIVMETA.InterrogationMethod)
setattr(PIVMETA, "Laser_Model", PIVMETA.LaserModel)
setattr(PIVMETA, "mask_generation", PIVMETA.MaskGeneration)
setattr(PIVMETA, "Multigrid", PIVMETA.Multigrid)
setattr(PIVMETA, "Multipass", PIVMETA.Multipass)
setattr(PIVMETA, "Outlier_Detection_Method", PIVMETA.OutlierDetectionMethod)
setattr(PIVMETA, "Outlier_Replacement_Scheme", PIVMETA.OutlierReplacementScheme)
setattr(PIVMETA, "piv_evaluation", PIVMETA.PIVEvaluation)
setattr(PIVMETA, "PIV_Hardware", PIVMETA.PIVHardware)
setattr(PIVMETA, "Piv_Software", PIVMETA.PIVSoftware)
setattr(PIVMETA, "Particle", PIVMETA.Particle)
setattr(PIVMETA, "Peak_Search_Method", PIVMETA.PeakSearchMethod)
setattr(PIVMETA, "piv_distribution", PIVMETA.PivDistribution)
setattr(PIVMETA, "piv_image_distribution", PIVMETA.PivImageDistribution)
setattr(PIVMETA, "piv_mask_distribution", PIVMETA.PivMaskDistribution)
setattr(PIVMETA, "piv_post_processing", PIVMETA.PivPostProcessing)
setattr(PIVMETA, "piv_pre_processing", PIVMETA.PivPreProcessing)
setattr(PIVMETA, "piv_processing_step", PIVMETA.PivProcessingStep)
setattr(PIVMETA, "piv_result_distribution", PIVMETA.PivResultDistribution)
setattr(PIVMETA, "PIV_Type", PIVMETA.PivType)
setattr(PIVMETA, "piv_validation", PIVMETA.PivValidation)
setattr(PIVMETA, "Singlepass", PIVMETA.Singlepass)
setattr(PIVMETA, "Synthetic_Particle", PIVMETA.SyntheticParticle)
setattr(PIVMETA, "Window_Weighting_Function", PIVMETA.WindowWeightingFunction)
setattr(PIVMETA, "has_standard_name", PIVMETA.hasStandardName)
setattr(PIVMETA, "outlier_replacement_scheme", PIVMETA.outlierReplacementScheme)
setattr(PIVMETA, "piv_image_type", PIVMETA.pivImageType)
setattr(PIVMETA, "window_weighting_function", PIVMETA.windowWeightingFunction)
setattr(PIVMETA, "filename_pattern", PIVMETA.filenamePattern)
setattr(PIVMETA, "flag_meanings", PIVMETA.flagMeanings)
setattr(PIVMETA, "flag_values", PIVMETA.flagValues)
setattr(PIVMETA, "fnumber", PIVMETA.fnumber)
setattr(PIVMETA, "material", PIVMETA.material)
setattr(PIVMETA, "number_of_records", PIVMETA.numberOfRecords)
setattr(PIVMETA, "experimental_image", PIVMETA.ExperimentalImage)
setattr(PIVMETA, "Gaussian_Window", PIVMETA.GaussianWindow)
setattr(PIVMETA, "Hamming_Window", PIVMETA.HammingWindow)
setattr(PIVMETA, "Hann_Window", PIVMETA.HannWindow)
setattr(PIVMETA, "Interpolation", PIVMETA.Interpolation)
setattr(PIVMETA, "left_right_flip", PIVMETA.LeftRightFlip)
setattr(PIVMETA, "millimetre_per_pixel", PIVMETA.MilliM_PER_PIXEL)
setattr(PIVMETA, "per_pixel", PIVMETA.PER_PIXEL)
setattr(PIVMETA, "Particle_Image_Velocimetry", PIVMETA.ParticleImageVelocimetry)
setattr(PIVMETA, "Particle_Tracking_Velocimetry", PIVMETA.ParticleTrackingVelocimetry)
setattr(PIVMETA, "re-evaluate_with_larger_sample", PIVMETA.ReEvaluateWithLargerSample)
setattr(PIVMETA, "spatial_resolution", PIVMETA.SpatialResolution)
setattr(PIVMETA, "split_image", PIVMETA.SplitImage)
setattr(PIVMETA, "Square_Window", PIVMETA.SquareWindow)
setattr(PIVMETA, "synthetic_image", PIVMETA.SyntheticImage)
setattr(PIVMETA, "top_bottom_flip", PIVMETA.TopBottomFlip)
setattr(PIVMETA, "try_lower_order_peaks", PIVMETA.TryLowerOrderPeaks)
setattr(PIVMETA, "Tukey_Window", PIVMETA.TukeyWindow)
setattr(PIVMETA, "Micro_PIV", PIVMETA.microPIV)
setattr(PIVMETA, "piv_first_peak_correlation_coefficient", PIVMETA.piv_first_peak_correlation_coefficient)
setattr(PIVMETA, "piv_correlation_coefficient", PIVMETA.piv_correlation_coefficient)
setattr(PIVMETA, "piv_second_peak_correlation_coefficient", PIVMETA.piv_second_peak_correlation_coefficient)
setattr(PIVMETA, "piv_third_peak_correlation_coefficient", PIVMETA.piv_third_peak_correlation_coefficient)
setattr(PIVMETA, "first_peak_x_displacement", PIVMETA.first_peak_x_displacement)
setattr(PIVMETA, "first_peak_y_displacement", PIVMETA.first_peak_y_displacement)
setattr(PIVMETA, "x_derivative_of_x_velocity", PIVMETA.x_derivative_of_x_velocity)
setattr(PIVMETA, "x_derivative_of_y_velocity", PIVMETA.x_derivative_of_y_velocity)
setattr(PIVMETA, "y_derivative_of_x_velocity", PIVMETA.y_derivative_of_x_velocity)
setattr(PIVMETA, "y_derivative_of_y_velocity", PIVMETA.y_derivative_of_y_velocity)
setattr(PIVMETA, "x_derivative_of_z_velocity", PIVMETA.x_derivative_of_z_velocity)
setattr(PIVMETA, "y_derivative_of_z_velocity", PIVMETA.y_derivative_of_z_velocity)
setattr(PIVMETA, "z_derivative_of_x_velocity", PIVMETA.z_derivative_of_x_velocity)
setattr(PIVMETA, "piv_flag", PIVMETA.piv_flag)
setattr(PIVMETA, "image_particle_density", PIVMETA.image_particle_density)
setattr(PIVMETA, "image_density", PIVMETA.image_density)
setattr(PIVMETA, "image_particle_diameter", PIVMETA.image_particle_diameter)
setattr(PIVMETA, "arithmetic_mean_of_image_particle_diameter", PIVMETA.arithmetic_mean_of_image_particle_diameter)
setattr(PIVMETA, "standard_deviation_of_image_particle_diameter", PIVMETA.standard_deviation_of_image_particle_diameter)
setattr(PIVMETA, "image_index", PIVMETA.image_index)
setattr(PIVMETA, "inplane_velocity", PIVMETA.inplane_velocity)
setattr(PIVMETA, "x_inplane_velocity", PIVMETA.x_inplane_velocity)
setattr(PIVMETA, "y_inplane_velocity", PIVMETA.y_inplane_velocity)
setattr(PIVMETA, "model_laser_sheet_thickness", PIVMETA.model_laser_sheet_thickness)
setattr(PIVMETA, "laser_sheet_thickness", PIVMETA.laser_sheet_thickness)
setattr(PIVMETA, "model_laser_sheet_shape_factor", PIVMETA.model_laser_sheet_shape_factor)
setattr(PIVMETA, "arithmetic_mean_of_seeding_particle_size", PIVMETA.arithmetic_mean_of_seeding_particle_size)
setattr(PIVMETA, "standard_deviation_of_seeding_particle_size", PIVMETA.standard_deviation_of_seeding_particle_size)
setattr(PIVMETA, "number_of_particles", PIVMETA.number_of_particles)
setattr(PIVMETA, "saturated_pixel_number", PIVMETA.saturated_pixel_number)
setattr(PIVMETA, "second_peak_x_displacement", PIVMETA.second_peak_x_displacement)
setattr(PIVMETA, "second_peak_y_displacement", PIVMETA.second_peak_y_displacement)
setattr(PIVMETA, "third_peak_x_displacement", PIVMETA.third_peak_x_displacement)
setattr(PIVMETA, "third_peak_y_displacement", PIVMETA.third_peak_y_displacement)
setattr(PIVMETA, "relative_time", PIVMETA.relative_time)
setattr(PIVMETA, "magnitude_of_velocity", PIVMETA.magnitude_of_velocity)
setattr(PIVMETA, "x_velocity", PIVMETA.x_velocity)
setattr(PIVMETA, "y_velocity", PIVMETA.y_velocity)
setattr(PIVMETA, "z_velocity", PIVMETA.z_velocity)
setattr(PIVMETA, "displacement", PIVMETA.displacement)
setattr(PIVMETA, "x_displacement", PIVMETA.x_displacement)
setattr(PIVMETA, "y_displacement", PIVMETA.y_displacement)
setattr(PIVMETA, "final_interrogation_window_overlap_size", PIVMETA.final_interrogation_window_overlap_size)
setattr(PIVMETA, "x_final_interrogation_window_overlap_size", PIVMETA.x_final_interrogation_window_overlap_size)
setattr(PIVMETA, "final_interrogation_window_size", PIVMETA.final_interrogation_window_size)
setattr(PIVMETA, "x_final_interrogation_window_size", PIVMETA.x_final_interrogation_window_size)
setattr(PIVMETA, "initial_interrogation_window_size", PIVMETA.initial_interrogation_window_size)
setattr(PIVMETA, "x_initial_interrogation_window_size", PIVMETA.x_initial_interrogation_window_size)
setattr(PIVMETA, "x_pixel_coordinate", PIVMETA.x_pixel_coordinate)
setattr(PIVMETA, "y_final_interrogation_window_overlap_size", PIVMETA.y_final_interrogation_window_overlap_size)
setattr(PIVMETA, "y_final_interrogation_window_size", PIVMETA.y_final_interrogation_window_size)
setattr(PIVMETA, "y_initial_interrogation_window_size", PIVMETA.y_initial_interrogation_window_size)
setattr(PIVMETA, "y_pixel_coordinate", PIVMETA.y_pixel_coordinate)
setattr(PIVMETA, "x_image_coordinate", PIVMETA.x_image_coordinate)
setattr(PIVMETA, "x_origin_offset", PIVMETA.x_origin_offset)
setattr(PIVMETA, "y_image_coordinate", PIVMETA.y_image_coordinate)
setattr(PIVMETA, "y_origin_offset", PIVMETA.y_origin_offset)
setattr(PIVMETA, "x_coordinate", PIVMETA.x_coordinate)
setattr(PIVMETA, "y_coordinate", PIVMETA.y_coordinate)
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
setattr(PIVMETA, "optical_magnification", PIVMETA.optical_magnification)
setattr(PIVMETA, "laser_pulse_delay", PIVMETA.laser_pulse_delay)