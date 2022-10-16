import Base from './Base';

const UploadFileSrcML = () => {
	return (
		<Base title="srcML Annotator" description="Instructions: please use the following file formats for upload: " subsection="upload_file_srcml" file_formats={["java", "cpp", "c", "h"]}/>
	)
}

export default UploadFileSrcML;