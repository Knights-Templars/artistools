from pathlib import Path
import os.path
import pandas as pd
from astropy import units as u
import numpy as np

import argparse
import artistools as at

MSUN = 1.989e33
CLIGHT = 2.99792458e10


def read_ejectasnapshot(pathtosnapshot):

    column_names = ['id', 'h', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'vstx', 'vsty', 'vstz', 'u',
                    'psi', 'alpha', 'pmass', 'rho', 'p', 'rst', 'tau', 'av', 'ye', 'temp',
                    'prev_rho(i)', 'ynue(i)', 'yanue(i)', 'enuetrap(i)', 'eanuetrap(i)',
                    'enuxtrap(i)', 'iwasequil(i, 1)', 'iwasequil(i, 2)', 'iwasequil(i, 3)']
    ejectasnapshot = pd.read_csv(pathtosnapshot / "ejectasnapshot.dat", delim_whitespace=True, header=None, dtype=float,
                                 names=column_names)
    # Everything is in geometric units here

    return ejectasnapshot


def get_snapshot_time_geomunits(pathtogriddata):
    import glob

    snapshotinfofile = glob.glob(str(Path(pathtogriddata) / "*_info.dat*"))
    if not snapshotinfofile:
        print("No info file found for dumpstep")
        quit()

    if len(snapshotinfofile) > 1:
        print('Too many sfho_info.dat files found')
        quit()
    snapshotinfofile = snapshotinfofile[0]

    if os.path.isfile(snapshotinfofile):
        with open(snapshotinfofile, "r") as fsnapshotinfo:
            line1 = fsnapshotinfo.readline()
            simulation_end_time_geomunits = float(line1.split()[2])
            print(f'Found simulation snapshot time to be {simulation_end_time_geomunits} '
                  f'({simulation_end_time_geomunits * 4.926e-6} s)')

    else:
        print("Could not find snapshot info file to get simulation time")
        quit()

    return simulation_end_time_geomunits


def read_griddat_file(pathtogriddata, targetmodeltime_days=None, minparticlespercell=0):
    griddatfilepath = Path(pathtogriddata) / "grid.dat"

    # Get simulation time for ejecta snapshot
    simulation_end_time_geomunits = get_snapshot_time_geomunits(pathtogriddata)

    griddata = pd.read_csv(griddatfilepath, delim_whitespace=True, comment='#', skiprows=3)
    griddata.rename(columns={'gridindex': 'inputcellid'}, inplace=True)
    # griddata in geom units
    griddata['rho'] = np.nan_to_num(griddata['rho'], nan=0.)

    if 'cellYe' in griddata:
        griddata['cellYe'] = np.nan_to_num(griddata['cellYe'], nan=0.)
    if 'Q' in griddata:
        griddata['Q'] = np.nan_to_num(griddata['Q'], nan=0.)

    factor_position = 1.478  # in km
    griddata['posx'] = (griddata['posx'] * factor_position) * (u.km).to(u.cm)
    griddata['posy'] = (griddata['posy'] * factor_position) * (u.km).to(u.cm)
    griddata['posz'] = (griddata['posz'] * factor_position) * (u.km).to(u.cm)

    griddata['rho'] = griddata['rho'] * 6.176e17  # convert to g/cm3

    with open(griddatfilepath, 'r') as gridfile:
        ngrid = int(gridfile.readline().split()[0])
        if ngrid != len(griddata['inputcellid']):
            print("length of file and ngrid don't match")
            quit()
        extratime_geomunits = float(gridfile.readline().split()[0])
        xmax = abs(float(gridfile.readline().split()[0]))
        xmax = (xmax * factor_position) * (u.km).to(u.cm)

    t_model_sec = (simulation_end_time_geomunits + extratime_geomunits) * 4.926e-6  # in seconds
    vmax = xmax / t_model_sec  # cm/s

    t_model_days = t_model_sec / (24. * 3600)  # in days
    print(f"t_model in days {t_model_days} ({t_model_sec} s)")

    if targetmodeltime_days is not None:
        timefactor = targetmodeltime_days / t_model_days
        griddata.eval('posx = posx * @timefactor', inplace=True)
        griddata.eval('posy = posy * @timefactor', inplace=True)
        griddata.eval('posz = posz * @timefactor', inplace=True)
        griddata.eval('rho = rho * @timefactor ** -3', inplace=True)
        print(f"Adjusting t_model to {targetmodeltime_days} days (factor {timefactor}) "
              "using homologous expansion of positions and densities")
        t_model_days = targetmodeltime_days

    if minparticlespercell > 0:
        ncoordgridx = round(len(griddata) ** (1. / 3.))
        xmax = griddata.posx.max()
        wid_init = 2 * xmax / ncoordgridx
        filter = np.logical_and(griddata.tracercount < minparticlespercell, griddata.rho > 0.)
        n_ignored = np.count_nonzero(filter)
        mass_ignored = griddata.loc[filter].rho.sum() * wid_init ** 3 / 1.989e33
        mass_orig = griddata.rho.sum() * wid_init ** 3 / 1.989e33

        print(f"Ignoring {n_ignored} nonempty cells ({mass_ignored:.2e} Msun, {mass_ignored / mass_orig * 100:.2f}% of mass) because they have < {minparticlespercell} tracer particles")
        griddata.loc[griddata.tracercount < minparticlespercell, ['rho', 'cellYe']] = 0., 0.

    print(f"Max tracers in a cell {max(griddata['tracercount'])}")

    return griddata, t_model_days, vmax


def mirror_model_in_axis(griddata):
    grid = round(len(griddata) ** (1. / 3.))

    rho = np.zeros((grid, grid, grid))
    cellYe = np.zeros((grid, grid, grid))
    tracercount = np.zeros((grid, grid, grid))
    Q = np.zeros((grid, grid, grid))

    i = 0
    for z in range(0, grid):
        for y in range(0, grid):
            for x in range(0, grid):
                rho[x, y, z] = griddata['rho'][i]
                cellYe[x, y, z] = griddata['cellYe'][i]
                tracercount[x, y, z] = griddata['tracercount'][i]
                Q[x, y, z] = griddata['Q'][i]
                i += 1

    for z in range(0, grid):
        z_mirror = grid-1 - z
        for y in range(0, grid):
            for x in range(0, grid):
                if z < 50:
                    rho[x, y, z] = rho[x, y, z]
                    cellYe[x, y, z] = cellYe[x, y, z]
                    tracercount[x, y, z] = tracercount[x, y, z]
                    Q[x, y, z] = Q[x, y, z]
                if z >= 50:
                    rho[x, y, z] = rho[x, y, z_mirror]
                    cellYe[x, y, z] = cellYe[x, y, z_mirror]
                    tracercount[x, y, z] = tracercount[x, y, z_mirror]
                    Q[x, y, z] = Q[x, y, z_mirror]

    rho_1d_array = np.zeros(len(griddata))
    cellYe_1d_array = np.zeros(len(griddata))
    tracercount_1d_array = np.zeros(len(griddata))
    Q_1d_array = np.zeros(len(griddata))
    i = 0
    for z in range(0, grid):
        for y in range(0, grid):
            for x in range(0, grid):
                rho_1d_array[i] = rho[x, y, z]
                cellYe_1d_array[i] = cellYe[x, y, z]
                tracercount_1d_array[i] = tracercount[x, y, z]
                Q_1d_array[i] = Q[x, y, z]
                i += 1

    griddata['rho'] = rho_1d_array
    griddata['cellYe'] = cellYe_1d_array
    griddata['tracercount'] = tracercount_1d_array
    griddata['Q'] = Q_1d_array

    return griddata


def add_mass_to_center(griddata, t_model_in_days, vmax, args):
    print(griddata)

    # Just (2021) Fig. 16 top left panel
    vel_hole = [0, 0.02, 0.05, 0.07, 0.09, 0.095, 0.1]
    mass_hole = [3e-4, 3e-4, 2e-4, 1e-4, 2e-5, 1e-5, 1e-9]
    mass_intergrated = np.trapz(y=mass_hole, x=vel_hole)  # Msun

    # # Just (2021) Fig. 16 4th down, left panel
    # vel_hole = [0, 0.02, 0.05, 0.1, 0.15, 0.16]
    # mass_hole = [4e-3, 2e-3, 1e-3, 1e-4, 6e-6, 1e-9]
    # mass_intergrated = np.trapz(y=mass_hole, x=vel_hole)  # Msun

    v_outer_hole = 0.1 * CLIGHT  # cm/s
    pos_outer_hole = v_outer_hole * t_model_in_days * (24. * 3600)  # cm
    vol_hole = 4 / 3 * np.pi * pos_outer_hole ** 3  # cm^3
    density_hole = (mass_intergrated * MSUN) / vol_hole  # g / cm^3
    print(density_hole)

    for i, cellid in enumerate(griddata['inputcellid']):
        # if pos < 0.1 c
        if ((np.sqrt(griddata['posx'][i] ** 2 + griddata['posy'][i] ** 2 + griddata['posz'][i] ** 2)) /
                (t_model_in_days * (24. * 3600)) / CLIGHT) < 0.1:
            # if griddata['rho'][i] == 0:
            print("Inner empty cells")
            print(cellid, griddata['posx'][i], griddata['posy'][i], griddata['posz'][i], griddata['rho'][i])
            griddata['rho'][i] += density_hole
            if griddata['cellYe'][i] < 0.4:
                griddata['cellYe'][i] = 0.4
            # print("Inner empty cells filled")
            print(cellid, griddata['posx'][i], griddata['posy'][i], griddata['posz'][i], griddata['rho'][i])

    return griddata


def makemodelfromgriddata(
        gridfolderpath=Path(), outputpath=Path(), targetmodeltime_days=None,
        minparticlespercell=10, getabundances=True, args=None):

    dfmodel, t_model_days, vmax = at.inputmodel.modelfromhydro.read_griddat_file(
        pathtogriddata=gridfolderpath, targetmodeltime_days=targetmodeltime_days, minparticlespercell=minparticlespercell)

    if getattr(args, 'fillcentralhole', False):
        dfmodel = at.inputmodel.modelfromhydro.add_mass_to_center(dfmodel, t_model_days, vmax, args)

    if getattr(args, 'getcellopacityfromYe', False):
        at.inputmodel.opacityinputfile.opacity_by_Ye(outputpath, dfmodel)
    if 'cellYe' in dfmodel:
        at.inputmodel.opacityinputfile.write_Ye_file(outputpath, dfmodel)
    if 'Q' in dfmodel and args.makeenergyinputfiles:
        at.inputmodel.energyinputfiles.write_Q_energy_file(outputpath, dfmodel)

    if getabundances:
        dfmodel, dfelabundances = at.inputmodel.rprocess_from_trajectory.add_abundancecontributions(
            gridcontribpath=gridfolderpath, dfmodel=dfmodel, t_model_days=t_model_days,
            minparticlespercell=minparticlespercell)
        print('Writing to abundances.txt...')
        at.inputmodel.save_initialabundances(dfelabundances=dfelabundances, abundancefilename=outputpath)
    else:
        ngrid = len(dfmodel['rho'])
        at.inputmodel.save_empty_abundance_file(ngrid)

    print('Writing to model.txt...')
    at.inputmodel.save_modeldata(
        modelpath=outputpath, dfmodel=dfmodel, t_model_init_days=t_model_days, dimensions=3, vmax=vmax)


def addargs(parser):
    parser.add_argument('-inputpath', '-i',
                        default='.',
                        help='Path of input files')
    parser.add_argument('-minparticlespercell',
                        default=10,
                        help='Minimum number of SPH particles in each cell (otherwise set rho=0)')
    parser.add_argument('-outputpath', '-o',
                        default='.',
                        help='Path for output model files')


def main(args=None, argsraw=None, **kwargs):
    if args is None:
        parser = argparse.ArgumentParser(
            formatter_class=at.CustomArgHelpFormatter,
            description='Create ARTIS format model from grid.dat.')

        addargs(parser)
        parser.set_defaults(**kwargs)
        args = parser.parse_args(argsraw)

    gridfolderpath = args.inputpath
    if not Path(gridfolderpath, 'grid.dat').is_file() or not Path(gridfolderpath, 'gridcontributions.txt').is_file():
        print('grid.dat and gridcontributions.txt are required')
        return
        # at.inputmodel.maptogrid.main()

    makemodelfromgriddata(
        gridfolderpath=gridfolderpath, outputpath=args.outputpath, minparticlespercell=args.minparticlespercell,
        targetmodeltime_days=1., getabundances=True)


if __name__ == "__main__":
    main()
