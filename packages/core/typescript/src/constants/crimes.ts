/**
 * NIBRS "A" Crime Types - standardized list
 */
export const NIBRS_CRIMES = [
  'Murder',
  'Rape',
  'Aggravated Assault',
  'Robbery',
  'Domestic Violence',
  'Weapons Law Violations',
  'Drug/Narcotic Violations',
  'Simple Assault',
  'Arson',
  'Burglary',
  'Motor Vehicle Theft',
  'Theft',
  'Law Violations',
  'Traffic Law Violations',
] as const;

export type NIBRSCrime = typeof NIBRS_CRIMES[number];

/**
 * ASHER Event Types
 */
export const ASHER_EVENTS = [
  'ASE',   // Active Shooter Event
  'IED',   // Improvised Explosive Device
  'VBIED', // Vehicle-Borne IED
  'VRA',   // Vehicle Ramming Attack
  'IID',   // Insider Incident
] as const;

export type ASHEREvent = typeof ASHER_EVENTS[number];