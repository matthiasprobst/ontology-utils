from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class HDF5(DefinedNamespace):
    # Generated with ontolutils version 0.13.1
    _fail = True
    AllSelection: URIRef
    AndSelection: URIRef
    ArrayDatatype: URIRef
    ArrayDimension: URIRef
    ArrayValue: URIRef
    AtomicDatatype: URIRef
    Attribute: URIRef
    BitfieldDatatype: URIRef
    CharacterSet: URIRef
    Chunk: URIRef
    ChunkDimension: URIRef
    ChunkMode: URIRef
    CompositeDatatype: URIRef
    CompositeValue: URIRef
    CompoundDatatype: URIRef
    CompoundDatatypeMember: URIRef
    CompoundValue: URIRef
    Coordinate: URIRef
    DataStream: URIRef
    Dataset: URIRef
    Dataspace: URIRef
    DataspaceDimension: URIRef
    Datatype: URIRef
    Dimension: URIRef
    DimensionSelection: URIRef
    EnumerationDatatype: URIRef
    EnumerationDatatypeMember: URIRef
    ErrorDetectionCheck: URIRef
    ExponentField: URIRef
    ExternalFile: URIRef
    FieldSpecification: URIRef
    File: URIRef
    FileAccessMode: URIRef
    FillTime: URIRef
    FillValueStatus: URIRef
    Filter: URIRef
    FilterDefault: URIRef
    FilterDeflate: URIRef
    FilterFletcher: URIRef
    FilterNBit: URIRef
    FilterSZip: URIRef
    FilterScaleOffset: URIRef
    FilterShuffle: URIRef
    FloatAttribute: URIRef
    FloatDatatype: URIRef
    FloatingPointNormalization: URIRef
    Group: URIRef
    HardLink: URIRef
    HyperSlab: URIRef
    IntegerAttribute: URIRef
    IntegerDatatype: URIRef
    Link: URIRef
    MantissaField: URIRef
    MessageTypeFlag: URIRef
    NameValuePair: URIRef
    NamedDatatype: URIRef
    NamedObject: URIRef
    NoneSelection: URIRef
    NotASelection: URIRef
    NotBSelection: URIRef
    OpaqueAttribute: URIRef
    OpaqueDatatype: URIRef
    OrSelection: URIRef
    Order: URIRef
    Padding: URIRef
    Point: URIRef
    PointSelection: URIRef
    PointValuePair: URIRef
    ReferenceDatatype: URIRef
    SZipCoding: URIRef
    ScalarDataspace: URIRef
    ScaleType: URIRef
    Selection: URIRef
    Sign: URIRef
    SignField: URIRef
    SimpleDataspace: URIRef
    SoftLink: URIRef
    StorageAllocation: URIRef
    StorageLayout: URIRef
    StringAttribute: URIRef
    StringDatatype: URIRef
    StringPadding: URIRef
    TimeDatatype: URIRef
    TransferMode: URIRef
    TypeClass: URIRef
    VariableLengthDatatype: URIRef
    XOrSelection: URIRef
    allocationTime: URIRef
    attribute: URIRef
    characterSet: URIRef
    chunk: URIRef
    chunkMode: URIRef
    compositeFillValue: URIRef
    compositeValue: URIRef
    coordinate: URIRef
    dataSource: URIRef
    dataTarget: URIRef
    dataspace: URIRef
    datatype: URIRef
    dimension: URIRef
    dimensionSelection: URIRef
    errorDetectionCheck: URIRef
    exponentField: URIRef
    externalLinkAccess: URIRef
    field: URIRef
    fillTime: URIRef
    fillValueStatus: URIRef
    filter: URIRef
    internalPadding: URIRef
    layout: URIRef
    link: URIRef
    linkedTo: URIRef
    lsbPadding: URIRef
    mantissaField: URIRef
    member: URIRef
    msbPadding: URIRef
    multiDimensionalIndex: URIRef
    normalization: URIRef
    notA: URIRef
    notB: URIRef
    order: URIRef
    point: URIRef
    previous: URIRef
    rootGroup: URIRef
    scaleType: URIRef
    selectionOn: URIRef
    sign: URIRef
    signField: URIRef
    stringPadding: URIRef
    szipEncoding: URIRef
    transferMode: URIRef
    typeClass: URIRef
    writtenRegion: URIRef
    xor: URIRef
    atomicFillValue: URIRef
    block: URIRef
    btreeIStoreSize: URIRef
    btreeLeaf: URIRef
    btreeRank: URIRef
    btreeRatioLeft: URIRef
    btreeRatioMiddle: URIRef
    btreeRatioRight: URIRef
    bufferSize: URIRef
    chunkCachePreemptionPolicy: URIRef
    chunkCacheSize: URIRef
    chunkCacheSlots: URIRef
    collectiveIOThreshold: URIRef
    compressionLevel: URIRef
    coordinateIndex: URIRef
    count: URIRef
    createIntermediateGroups: URIRef
    currentSize: URIRef
    data: URIRef
    deflateLevel: URIRef
    dimensionIndex: URIRef
    ebias: URIRef
    externalLinkCacheSize: URIRef
    externalLinkPrefix: URIRef
    globalFreelistVersion: URIRef
    hyperVectorSize: URIRef
    iStoreK: URIRef
    index: URIRef
    index_0: URIRef
    index_1: URIRef
    index_10: URIRef
    index_11: URIRef
    index_12: URIRef
    index_13: URIRef
    index_14: URIRef
    index_15: URIRef
    index_16: URIRef
    index_17: URIRef
    index_18: URIRef
    index_19: URIRef
    index_2: URIRef
    index_20: URIRef
    index_21: URIRef
    index_22: URIRef
    index_23: URIRef
    index_24: URIRef
    index_25: URIRef
    index_26: URIRef
    index_27: URIRef
    index_28: URIRef
    index_29: URIRef
    index_3: URIRef
    index_30: URIRef
    index_31: URIRef
    index_4: URIRef
    index_5: URIRef
    index_6: URIRef
    index_7: URIRef
    index_8: URIRef
    index_9: URIRef
    initialSize: URIRef
    isVariableLength: URIRef
    linkedChunkThreshold: URIRef
    maximumLinkTraversals: URIRef
    maximumSize: URIRef
    metaBlockSize: URIRef
    minimumSize: URIRef
    name: URIRef
    offset: URIRef
    pixelsPerBlock: URIRef
    position: URIRef
    precision: URIRef
    preserve: URIRef
    rank: URIRef
    scaleFactor: URIRef
    sharedObjectHeaderVersion: URIRef
    sieveBufferSize: URIRef
    size: URIRef
    sizeOfAddress: URIRef
    sizeOfSize: URIRef
    smallDataBlockSize: URIRef
    start: URIRef
    stride: URIRef
    superBlockVersion: URIRef
    symbolTableNodeSize: URIRef
    symbolTableTreeRank: URIRef
    symbolTableVersion: URIRef
    trackTimes: URIRef
    userBlockSize: URIRef
    value: URIRef

    _NS = Namespace("http://purl.allotrope.org/ontologies/hdf5/1.8#")