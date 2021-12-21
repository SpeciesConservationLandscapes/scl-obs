--SCL - Camera Trap - Duplicate Location and Year (Grid)

;
WITH CTDuplicate As
(
SELECT
	CI_GridCellID
	,YEAR(CI_CameraTrapObservation.ObservationDateTime) AS [Year]
	--,COUNT(*) AS [Instances]

FROM
	CI_CameraTrapObservation
	INNER JOIN CI_CameraTrapDeployment ON (CI_CameraTrapObservation.CI_CameraTrapDeploymentID=CI_CameraTrapDeployment.CI_CameraTrapDeploymentID)
	INNER JOIN CI_UploadedFile ON (CI_CameraTrapObservation.CI_UploadedFileID=CI_UploadedFile.CI_UploadedFileID)

WHERE
	CI_CameraTrapDeployment.Archive=0
	AND CI_CameraTrapObservation.Archive=0
	AND CI_UploadedFile.CI_ScenarioID IS NULL
	AND CI_CameraTrapDeployment.CI_GridCellID IS NOT NULL

GROUP BY
	CI_GridCellID
	,YEAR(CI_CameraTrapObservation.ObservationDateTime)

HAVING COUNT(DISTINCT CI_CameraTrapObservation.CI_CameraTrapObservationID)>1
)

SELECT
	YEAR(CI_CameraTrapObservation.ObservationDateTime) AS [Year]
	,CI_GridCell.CI_GridCellCode AS [Grid Cell Label]
	--,CI_CameraTrapDeployment.Reference
	,CI_CameraTrapDeployment.*
	,CI_CameraTrapObservation.*

FROM
	CI_CameraTrapObservation
	INNER JOIN CI_CameraTrapDeployment ON (CI_CameraTrapObservation.CI_CameraTrapDeploymentID=CI_CameraTrapDeployment.CI_CameraTrapDeploymentID)
	INNER JOIN CI_GridCell ON (CI_CameraTrapDeployment.CI_GridCellID=CI_GridCell.CI_GridCellID)
	INNER JOIN CTDuplicate ON
	(
		CI_CameraTrapDeployment.CI_GridCellID=CTDuplicate.CI_GridCellID
		AND
		YEAR(CI_CameraTrapObservation.ObservationDateTime)=CTDuplicate.[Year]
	)
	INNER JOIN CI_UploadedFile ON (CI_CameraTrapObservation.CI_UploadedFileID=CI_UploadedFile.CI_UploadedFileID)

WHERE
	CI_CameraTrapDeployment.Archive=0
	AND CI_CameraTrapObservation.Archive=0
	AND CI_UploadedFile.CI_ScenarioID IS NULL
	AND CI_CameraTrapDeployment.CI_GridCellID IS NOT NULL

ORDER BY 1,3