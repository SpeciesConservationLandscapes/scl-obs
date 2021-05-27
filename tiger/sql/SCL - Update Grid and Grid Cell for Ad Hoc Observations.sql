SELECT
	CI_AdHocObservation.CI_GridID
	,CI_AdHocObservation.CI_GridCellID
	,CI_GridCell.CI_GridCellCode
	,G2.CI_GridCellCode
	,G2.CI_GridID
	,G2.CI_GridCellID
FROM
	CI_AdHocObservation
	INNER JOIN CI_GridCell ON (CI_AdHocObservation.CI_GridCellID=CI_GridCell.CI_GridCellID)
	INNER JOIN CI_GridCell G2 ON (CI_GridCell.CI_GridCellCode=G2.CI_GridCellCode AND G2.CI_GridID=19)
WHERE
	CI_AdHocObservation.CI_GridID=18

/*
UPDATE CI_AdHocObservation
SET CI_GridID=G2.CI_GridID
	,CI_GridCellID=G2.CI_GridCellID
FROM
	CI_AdHocObservation
	INNER JOIN CI_GridCell ON (CI_AdHocObservation.CI_GridCellID=CI_GridCell.CI_GridCellID)
	INNER JOIN CI_GridCell G2 ON (CI_GridCell.CI_GridCellCode=G2.CI_GridCellCode AND G2.CI_GridID=19)
WHERE
	CI_AdHocObservation.CI_GridID=18
*/