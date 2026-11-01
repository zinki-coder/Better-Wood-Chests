package betterwoodchests.modid;

import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.block.state.BlockState;

public class WoodChestBlockEntity extends ChestBlockEntity {
    public WoodChestBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.WOOD_CHEST, pos, state);
    }
}
