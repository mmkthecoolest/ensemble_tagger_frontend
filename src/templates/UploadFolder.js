import AnnotateFolder from './AnnotateFolder';

const UploadFolder = () => {
	return (
		<AnnotateFolder title="Upload a Folder" description="Instructions: please use the following file formats for upload: " file_formats={["zip", "tar.gz"]} buttonList={{ "Annotate Folder with Tagger": ["upload_folder_annotate", "upload_folder_annotate_download"], "Annotate Folder with srcML": ["upload_folder_srcml", "upload_folder_srcml_download"]}} />
	)
}

export default UploadFolder;