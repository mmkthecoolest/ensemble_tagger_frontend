import AnnotateFile from './AnnotateFile';

const UploadFile = () => {
	return (
		<AnnotateFile title="Upload a File" description="Instructions: please use the following file formats for upload: " file_formats={["java", "cpp", "c", "h"]} buttonList={{ "Annotate File with Tagger": "upload_file_annotate", "Annotate File with srcML": "upload_file_srcml" }} />
	)
}

export default UploadFile;